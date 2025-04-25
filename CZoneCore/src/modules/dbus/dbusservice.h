#ifndef DBUS_SERVICE_H
#define DBUS_SERVICE_H

#include "utils/logger.h"

#include <memory>
#include <unordered_set>
#include <sdbus-c++/sdbus-c++.h>
#include <functional>
#include <string>

class DbusService {
public:
    DbusService();
    ~DbusService();
    void initialize();
    void run();
    void stop();

    // template<typename Func, typename... SignalArgs>
    // void registerService(const std::string& methodName, const std::string& interfaceSuffix, Func methodImplemented, const std::string& signalName);
    // template<typename Func, typename... SignalArgs>
    // void registerService(const std::string& methodName, const std::string& interfaceSuffix, Func methodImplemented);

    template<typename Func, typename... SignalArgs>
    void registerService(const std::string& methodName, const std::string& interfaceSuffix, Func methodImplemented, const std::string& signalName) {

        if (methodName.empty()) {
            BOOST_LOG_TRIVIAL(error) << "Method name is empty";
            throwError("Method name is empty");
        }
        if (interfaceSuffix.empty()) {
            BOOST_LOG_TRIVIAL(error) << "Interface suffix is empty";
            throwError("Interface suffix is empty");
        }
        if (signalName.empty()) {
            BOOST_LOG_TRIVIAL(error) << "Signal name is empty";
            throwError("Signal name is empty");
        }

        auto methodEndpoint = m_servicename + "." + interfaceSuffix + "." + methodName;
        auto signalEndpoint = m_servicename + "." + interfaceSuffix + "." + signalName;

        if (m_registeredMethods.find(methodEndpoint) != m_registeredMethods.end()) {
            BOOST_LOG_TRIVIAL(error) << "Method already registered: " + methodEndpoint;
            throwError("Method already registered");
        }

        if (m_registeredSignals.find(signalEndpoint) != m_registeredSignals.end()) {
            BOOST_LOG_TRIVIAL(error) << "Signal already registered: " + signalEndpoint;
            throwError("Signal already registered");
        }

        registerMethod(methodName, methodImplemented, interfaceSuffix);
        m_registeredMethods.insert(methodEndpoint);
        BOOST_LOG_TRIVIAL(debug) << "Method registered: " + methodEndpoint;

        registerSignal<SignalArgs...>(signalName, interfaceSuffix);
        m_registeredSignals.insert(signalEndpoint);
        BOOST_LOG_TRIVIAL(debug) << "Signal registered: " + signalEndpoint;
    }

    template<typename Func, typename... SignalArgs>
    void registerService(const std::string& methodName, const std::string& interfaceSuffix, Func methodImplemented) {
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

        registerMethod(methodName, methodImplemented, interfaceSuffix);
        m_registeredMethods.insert(methodEndpoint);
        BOOST_LOG_TRIVIAL(debug) << "Method registered: " + methodEndpoint;
    }

private:
    const std::string m_objectpath = "/org/navico/CzoneCpp";
    const std::string m_servicename = "org.navico.CzoneCpp";

    std::unique_ptr<sdbus::IConnection> m_connection;
    std::unique_ptr<sdbus::IObject> m_object;

    std::unordered_set<std::string> m_registeredSignals;
    std::unordered_set<std::string> m_registeredMethods;

    void throwError(const std::string& errorMessage);

    void initializeServiceMethods();

    // template<typename Func>
    // void registerMethod(const std::string& methodName, Func methodImplementation, const std::string& interface);

    // template <typename... Args>
    // void registerSignal(const std::string& signalName, const std::string& interface);

    template <typename Func>
    void registerMethod(const std::string& methodName, Func methodImplementation, const std::string& interfaceSuffix) {
        m_object->addVTable(sdbus::registerMethod(methodName).implementedAs(methodImplementation))
            .forInterface(m_servicename + "." + interfaceSuffix);
    }

    template <typename... Args>
    void registerSignal(const std::string& signalName, const std::string& interfaceSuffix) {
        m_object->addVTable(sdbus::registerSignal(signalName).withParameters<Args...>())
            .forInterface(m_servicename + "." + interfaceSuffix);
    }

    std::string echo(const std::string& message) { return "Echo: " + message; }
    std::string version() { return "1.0.0"; }
};


#endif // DBUS_SERVICE_H