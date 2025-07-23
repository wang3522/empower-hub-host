#include "utils/asyncworker.h"
#include "utils/logger.h"

WorkerPool::WorkerPool() : m_threadPoolSize(THREAD_POOL_SIZE) { initializeThreadPool(); }

WorkerPool::WorkerPool(int size) : m_threadPoolSize(size) { initializeThreadPool(); }

WorkerPool::~WorkerPool() {
  shutdownThreadPool();

  {
    std::lock_guard<std::mutex> lock(m_threadTrackingMutex);

    for (auto &future : m_activeFutures) {
      if (future.valid()) {
        future.wait();
      }
    }
  }
}

void WorkerPool::initializeThreadPool() {
  m_shutdown = false;

  for (int i = 0; i < m_threadPoolSize; ++i) {
    m_eventThreadPool.emplace_back(&WorkerPool::eventWorker, this);
  }
}

void WorkerPool::shutdownThreadPool() {
  m_shutdown = true;

  m_eventCondition.notify_all();

  for (auto &thread : m_eventThreadPool) {
    if (thread.joinable()) {
      thread.join();
    }
  }

  m_eventThreadPool.clear();
}

void WorkerPool::eventWorker() {
  while (!m_shutdown) {
    std::function<void()> task;

    {
      std::unique_lock<std::mutex> lock(m_eventQueueMutex);

      m_eventCondition.wait(lock, [this] { return !m_eventQueue.empty() || m_shutdown; });

      if (m_shutdown && m_eventQueue.empty()) {
        break;
      }

      if (!m_eventQueue.empty()) {
        task = std::move(m_eventQueue.front());
        m_eventQueue.pop();
      }
    }

    if (task) {
      try {
        task();
      } catch (const std::exception &e) {
        BOOST_LOG_TRIVIAL(error) << "Event worker exception: " << e.what();
      } catch (...) {
        BOOST_LOG_TRIVIAL(error) << "Event worker unknown exception";
      }
    }
  }
}

void WorkerPool::trackFuture(std::future<void> &&future) {
  std::lock_guard<std::mutex> lock(m_threadTrackingMutex);
  m_activeFutures.emplace_back(std::move(future));
}

void WorkerPool::addTask(std::function<void()> task) {
  {
    std::lock_guard<std::mutex> lock(m_eventQueueMutex);
    m_eventQueue.push(std::move(task));
  }

  m_eventCondition.notify_one();
}

void WorkerPool::addTaskOnThread(std::function<void()> task) {
  auto future = std::async(std::launch::async, std::move(task));
  trackFuture(std::move(future));
}