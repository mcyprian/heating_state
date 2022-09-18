import enum


class Devices(enum.Enum):
    suteren = "T. Suterén 14°"
    prizemie_chodba = "0.03 Prízemie chodba"
    prizemie_obyv_kuchyna = "0.01, 0.02 Príz. obýv, kuchyňa"
    prizemie_hostovska = "0.04 Prízemie hosťovská"
    prizemie_kupelna = "0.06 Prízemie kúpelňa"
    poschodie_chodba = "1.05 Posch chodba nepripoj"
    poschodie_satnik = "1.03 Poschodie šatník"
    poschodie_mala_detska = "1.02 Poschodie malá detská"
    poschodie_kupelna = "1.06 Poschodie kúpeľňa"
    poschodie_spalna = "1.04 Poschodie spálňa"
    poschodie_detska = "1.01 Poschodie detská veľká"


GROUND_FLOOR_DEVICES = (
    Devices.suteren,
    Devices.prizemie_chodba,
    Devices.prizemie_obyv_kuchyna,
    Devices.prizemie_hostovska,
    Devices.prizemie_kupelna,
)

FIRST_FLOOR_DEVIDES = (
    Devices.poschodie_chodba,
    Devices.poschodie_satnik,
    Devices.poschodie_mala_detska,
    Devices.poschodie_kupelna,
    Devices.poschodie_spalna,
    Devices.poschodie_detska,
)


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
