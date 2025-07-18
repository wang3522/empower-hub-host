#pragma once

#include <atomic>
#include <condition_variable>
#include <future>
#include <memory>
#include <mutex>
#include <queue>
#include <thread>
#include <vector>

class WorkerPool {
public:
  WorkerPool();
  WorkerPool(int size);
  ~WorkerPool();

  bool isShutdown() const { return m_shutdown.load(); }
  void addTask(std::function<void()>);
  void addTaskOnThread(std::function<void()>);

private:
  // thread pool for event
  std::vector<std::thread> m_eventThreadPool;
  std::vector<std::future<void>> m_activeFutures;
  std::queue<std::function<void()>> m_eventQueue;
  std::mutex m_eventQueueMutex;
  std::condition_variable m_eventCondition;
  std::atomic<bool> m_shutdown{false};

  std::mutex m_threadTrackingMutex;

  // Thread pool size
  static constexpr int THREAD_POOL_SIZE = 4;
  int m_threadPoolSize;

  void initializeThreadPool();
  void shutdownThreadPool();
  void eventWorker();
  void trackFuture(std::future<void> &&future);
};
