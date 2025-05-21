#include "utils/logger.h"
#include "modules/dbus/dbusservice.h"

#include <unordered_map>
#include <vector>

DbusService::DbusService(const char* name, const char* path): m_servicename(name), m_objectpath(path) {
    try {
        // m_connection = sdbus::createSessionBusConnection(sdbus::ServiceName(m_servicename));
        m_connection = sdbus::createSystemBusConnection(sdbus::ServiceName(m_servicename));
        m_object = sdbus::createObject(*m_connection, sdbus::ObjectPath(m_objectpath));
    }
    catch (const std::exception& e) {
        BOOST_LOG_TRIVIAL(error) << std::string("Failed to create DbusService: %s") + e.what();
        throwError("Failed to create DbusService");
    }

}

DbusService::~DbusService() {
    if (m_object) {
        m_object->unregister();
    }
    BOOST_LOG_TRIVIAL(info) << "DbusService destroyed";
}

void DbusService::initialize() {
    if (!m_connection) {
        BOOST_LOG_TRIVIAL(error) << "DbusService connection is not initialized";
        throwError("Failed to initialize DbusService");
    }
    if (!m_object) {
        BOOST_LOG_TRIVIAL(error) << "DbusService object is not initialized";
        throwError("Failed to initialize DbusService");
    }
    initializeServiceMethods();
    BOOST_LOG_TRIVIAL(debug) << "DbusService methods registered...";
}

void DbusService::run() {
    if (!m_connection) {
        BOOST_LOG_TRIVIAL(error) << "DbusService connection is not initialized";
        return;
    }
    if (!m_object) {
        BOOST_LOG_TRIVIAL(error) << "DbusService object is not initialized";
        return;
    }
    BOOST_LOG_TRIVIAL(debug) << "DbusService starting...";

    m_connection->enterEventLoopAsync();
    BOOST_LOG_TRIVIAL(debug) << "DbusService running";
}

void DbusService::stop() {
    m_connection->leaveEventLoop();
    BOOST_LOG_TRIVIAL(info) << "DbusService stopped";
}

void DbusService::throwError(const std::string& errorMessage) {
    throw sdbus::Error(sdbus::Error::Name{ m_servicename + ".Error" }, errorMessage);
}


void DbusService::initializeServiceMethods() {
    registerService("concatenate",
        "debug",
        [this](const std::vector<int>& numbers, const std::string& separator) {
            if (numbers.empty())
                this->throwError("No numbers provided");

            std::string result;
            for (auto number : numbers) {
                result += (result.empty() ? std::string() : separator) + std::to_string(number);
            }

            this->m_object->emitSignal("concatenated")
                .onInterface("org.navico.HubN2K")
                .withArguments(result);

            return result;
        },
        "concatenated");

    registerService("version",
        "status",
        [this]() {
            return this->version();
        });

    registerService("echo",
        "debug",
        [this](const std::string& message) {
            return this->echo(message);
        });
}