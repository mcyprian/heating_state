import enum


class Devices(enum.Enum):
    prizemie_chodba = "0.03 Prízemie chodba"
    suteren = "T. Suterén"


class DeviceProperties(enum.Enum):
    temperature = "ep_9:sIT600TH:LocalTemperature_x100"
    running_state = "ep_9:sIT600TH:RunningState"

    cloudy_setpoint = "ep_9:sIT600TH:CloudySetpoint_x100"
    sunny_setpoint = "ep_9:sIT600TH:SunnySetpoint_x100"
    cooling_control = "ep_9:sIT600TH:CoolingControl"
    heating_control = "ep_9:sIT600TH:HeatingControl"
    hold_type = "ep_9:sIT600TH:HoldType"
    sensor_probe = "ep_9:sIT600TH:OUTSensorProbe"
    schedule_type = "ep_9:sIT600TH:ScheduleType"
    running_mode = "ep_9:sIT600TH:RunningMode"
    system_mode = "ep_9:sIT600TH:SystemMode"
    leave_network = "ep_9:sZDO:LeaveNetwork"
    online_status = "ep_9:sZDOInfo:OnlineStatus_i"
