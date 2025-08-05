#ifndef DBUS_SERVICE_H
#define DBUS_SERVICE_H

#include "utils/logger.h"

#include <functional>
#include <memory>
#include <sdbus-c++/sdbus-c++.h>
#include <string>
#include <unordered_set>

class DbusService {
public:
  DbusService(const char *name, const char *path);
  ~DbusService();
  void initialize();
  void run();
  void stop();

  template <typename... SignalArgs>
  void registerSignal(const std::string &signalName, const std::string &interfaceSuffix) {
    if (interfaceSuffix.empty()) {
      BOOST_LOG_TRIVIAL(error) << "Interface suffix is empty";
      return;
    }
    if (signalName.empty()) {
      BOOST_LOG_TRIVIAL(error) << "Signal name is empty";
      return;
    }

    auto signalEndpoint = m_servicename + "." + interfaceSuffix + "." + signalName;

    if (m_registeredSignals.find(signalEndpoint) != m_registeredSignals.end()) {
      BOOST_LOG_TRIVIAL(error) << "Signal already registered: " + signalEndpoint;
      return;
    }

    addSignalToVTable<SignalArgs...>(signalName, interfaceSuffix);
    m_registeredSignals.insert(signalEndpoint);
    BOOST_LOG_TRIVIAL(debug) << "Signal registered: " + signalEndpoint;
  }

  template <typename Func>
  void registerService(const std::string &methodName, const std::string &interfaceSuffix, Func methodImplemented) {
    if (methodName.empty()) {
      BOOST_LOG_TRIVIAL(error) << "Method name is empty";
      throwError("Method name is empty");
    }
    if (interfaceSuffix.empty()) {
      BOOST_LOG_TRIVIAL(error) << "Interface suffix is empty";
      throwError("Interface suffix is empty");
    }

    auto methodEndpoint = m_servicename + "." + interfaceSuffix + "." + methodName;
    if (m_registeredMethods.find(methodEndpoint) != m_registeredMethods.end()) {
      BOOST_LOG_TRIVIAL(error) << "Method already registered: " + methodEndpoint;
      throwError("Method already registered");
    }

    addMethodToVTable(methodName, methodImplemented, interfaceSuffix);
    m_registeredMethods.insert(methodEndpoint);
    BOOST_LOG_TRIVIAL(debug) << "Method registered: " + methodEndpoint;
  }

  void emitSignal(const std::string &signalName, const std::string &interfaceSuffix, const std::string &result) {
    auto signalEndpoint = m_servicename + "." + interfaceSuffix + "." + signalName;
    if (m_registeredSignals.find(signalEndpoint) != m_registeredSignals.end()) {
      m_object->emitSignal(signalName).onInterface(m_servicename + "." + interfaceSuffix).withArguments(result);
    }
  }

  void throwError(const std::string &errorMessage);

private:
  const std::string m_objectpath = "/org/navico/HubN2K";
  const std::string m_servicename = "org.navico.HubN2K";

  std::unique_ptr<sdbus::IConnection> m_connection;
  std::unique_ptr<sdbus::IObject> m_object;

  std::unordered_set<std::string> m_registeredSignals;
  std::unordered_set<std::string> m_registeredMethods;

  template <typename Func>
  void addMethodToVTable(const std::string &methodName, Func methodImplementation, const std::string &interfaceSuffix) {
    m_object->addVTable(sdbus::registerMethod(methodName).implementedAs(methodImplementation))
        .forInterface(m_servicename + "." + interfaceSuffix);
  }

  template <typename... Args>
  void addSignalToVTable(const std::string &signalName, const std::string &interfaceSuffix) {
    m_object->addVTable(sdbus::registerSignal(signalName).withParameters<Args...>())
        .forInterface(m_servicename + "." + interfaceSuffix);
  }
};

#endif // DBUS_SERVICE_H