from .metering_device import MeteringDevice


class DC(MeteringDevice):
    capacity: int
    show_state_of_charge: int
    show_temperature: int
    show_time_remainig: int
