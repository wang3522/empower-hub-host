#include "core/coremanager.h"
#include "modules/czone/czoneinterface.h"
#include "utils/common.h"
#include "utils/logger.h"

#include <App/ContourZoneProductIds.h>

#include <chrono>
#include <cstdlib>
#include <thread>

void setCANBaudRate(const std::string &iface, int baudrate) {
  std::string cmd = "sudo ip link set " + iface +
                    " down && "
                    "sudo ip link set " +
                    iface + " type can bitrate " + std::to_string(baudrate) +
                    " && "
                    "sudo ip link set " +
                    iface + " up";
  auto i = system(cmd.c_str());
  if (i != 0) {
    BOOST_LOG_TRIVIAL(error) << "Failed to set CAN baud rate on interface " << iface;
    throw std::runtime_error("Failed to set CAN baud rate");
    return;
  }
  BOOST_LOG_TRIVIAL(debug) << "setCANBaudRate: CAN baud rate set to " << baudrate << " on interface " << iface;
}

CoreManager::CoreManager()
    : m_running(false),
      m_canService(CanService::getInstance()),
      m_dbusService(std::make_shared<DbusService>(CzoneSystemConstants::DBUS_CZONE_SERVICENAME,
                                                  CzoneSystemConstants::DBUS_CZONE_OBJECTPATH)) {}

CoreManager::~CoreManager() { stop(); }

CoreManager &CoreManager::getInstance() {
  static CoreManager _instance;
  return _instance;
}

void CoreManager::start() {
  if (m_running.load()) {
    BOOST_LOG_TRIVIAL(error) << "CoreManager is already running!";
    return;
  }

  auto dipswitch = CzoneSystemConstants::DEFAULT_DIPSWITCH;
  auto insecure = true;
  uint32_t uniqueId = mtEuropa;
  uint16_t productId = CZ_PRODUCT_CODE_EUROPA;
  uint8_t lastSourceAddress = 0;
  auto &can_channel = CzoneSystemConstants::DEFAULT_CAN_CHANNEL;
  auto &nema_channel = CzoneSystemConstants::DEFAULT_NEMA_CHANNEL;
  auto &mercury_engine = CzoneSystemConstants::DEFAULT_MERCURY_ENGINE_S;

  // [x] reset can network
  setCANBaudRate(can_channel, 250000);

  // Czone Settings
  auto &czonesettings = CzoneSettings::getInstance();
  auto stored_dipswitch = czonesettings.getDipswitch();
  if ((stored_dipswitch == 0) && (dipswitch != 0)) {
    stored_dipswitch = dipswitch;
    czonesettings.setDipswitch(stored_dipswitch);
  }
  czonesettings.setInsecure(insecure);

  // can init
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Initializing";
  auto czoneInterface = std::make_shared<CzoneInterface>(czonesettings, m_canService.getCanServiceMutex());

  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Interface intializing.";
  czoneInterface->init(stored_dipswitch, uniqueId);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Interface initialized.";

  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService intializing.";
  m_canService.initialise(&czonesettings, czoneInterface.get(), can_channel, stored_dipswitch, uniqueId, productId,
                          lastSourceAddress, nema_channel, mercury_engine);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService initialized.";

  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Starting CanService...";
  m_canService.service(true);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService started.";

  // dbus init and register method
  m_dbusService->initialize();

  czoneInterface->registerDbus(m_dbusService);

  m_dbusService->run();

  m_running.store(true);
  this->run();
}

void CoreManager::stop() {
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::stop: Stopping CoreManager...";

  m_canService.setShutdownSignal(true);
  m_canService.service(false);
  m_canService.reset();

  if (m_dbusService) {
    m_dbusService->stop();
    m_dbusService.reset();
  }
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::stop: DbusService stopped.";

  if (!m_running.load()) {
    return;
  }
  m_running.store(false);
}

void CoreManager::run() {
  while (m_running.load()) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::run: CoreManager has stopped.";
}