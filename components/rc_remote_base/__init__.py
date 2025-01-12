import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components.remote_base import RCSwitchData, RemoteReceiverTrigger, RemoteTransmitterDumper, ns
from esphome.const import (
    CONF_TRIGGER_ID,
)
from esphome.core import coroutine
from esphome.schema_extractors import SCHEMA_EXTRACT, schema_extractor
from esphome.util import Registry, SimpleRegistry

# AUTO_LOAD = ["binary_sensor"]

CONF_RECEIVER_ID = "receiver_id"
# CONF_TRANSMITTER_ID = "transmitter_id"
# CONF_FIRST = "first"

# ns = remote_base_ns = cg.esphome_ns.namespace("remote_base")
# RemoteProtocol = ns.class_("RemoteProtocol")
# RemoteReceiverListener = ns.class_("RemoteReceiverListener")
# RemoteReceiverBinarySensorBase = ns.class_(
#     "RemoteReceiverBinarySensorBase", binary_sensor.BinarySensor, cg.Component
# )
# RemoteReceiverTrigger = ns.class_(
#     "RemoteReceiverTrigger", automation.Trigger, RemoteReceiverListener
# )
# RemoteTransmitterDumper = ns.class_("RemoteTransmitterDumper")
# RemoteTransmittable = ns.class_("RemoteTransmittable")
# RemoteTransmitterActionBase = ns.class_(
#     "RemoteTransmitterActionBase", RemoteTransmittable, automation.Action
# )
# RemoteReceiverBase = ns.class_("RemoteReceiverBase")
# RemoteTransmitterBase = ns.class_("RemoteTransmitterBase")


# def templatize(value):
#     if isinstance(value, cv.Schema):
#         value = value.schema
#     ret = {}
#     for key, val in value.items():
#         ret[key] = cv.templatable(val)
#     return cv.Schema(ret)


# REMOTE_LISTENER_SCHEMA = cv.Schema(
#     {
#         cv.GenerateID(CONF_RECEIVER_ID): cv.use_id(RemoteReceiverBase),
#     }
# )


# REMOTE_TRANSMITTABLE_SCHEMA = cv.Schema(
#     {
#         cv.GenerateID(CONF_TRANSMITTER_ID): cv.use_id(RemoteTransmitterBase),
#     }
# )


# async def register_listener(var, config):
#     receiver = await cg.get_variable(config[CONF_RECEIVER_ID])
#     cg.add(receiver.register_listener(var))


# async def register_transmittable(var, config):
#     transmitter_ = await cg.get_variable(config[CONF_TRANSMITTER_ID])
#     cg.add(var.set_transmitter(transmitter_))


# def register_binary_sensor(name, type, schema):
#     return BINARY_SENSOR_REGISTRY.register(name, type, schema)


def register_trigger(name, type, data_type):
    validator = automation.validate_automation(
        {
            cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(type),
            cv.Optional(CONF_RECEIVER_ID): cv.invalid(
                "This has been removed in ESPHome 2022.3.0 and the trigger attaches directly to the parent receiver."
            ),
        }
    )
    registerer = TRIGGER_REGISTRY.register(f"on_{name}", validator)

    def decorator(func):
        async def new_func(config):
            var = cg.new_Pvariable(config[CONF_TRIGGER_ID])
            await coroutine(func)(var, config)
            await automation.build_automation(var, [(data_type, "x")], config)
            return var

        return registerer(new_func)

    return decorator


def register_dumper(name, type):
    registerer = DUMPER_REGISTRY.register(name, type, {})

    def decorator(func):
        async def new_func(config, dumper_id):
            var = cg.new_Pvariable(dumper_id)
            await coroutine(func)(var, config)
            return var

        return registerer(new_func)

    return decorator


# def validate_repeat(value):
#     if isinstance(value, dict):
#         return cv.Schema(
#             {
#                 cv.Required(CONF_TIMES): cv.templatable(cv.positive_int),
#                 cv.Optional(CONF_WAIT_TIME, default="25ms"): cv.templatable(
#                     cv.positive_time_period_microseconds
#                 ),
#             }
#         )(value)
#     return validate_repeat({CONF_TIMES: value})


# BASE_REMOTE_TRANSMITTER_SCHEMA = cv.Schema(
#     {
#         cv.Optional(CONF_REPEAT): validate_repeat,
#     }
# ).extend(REMOTE_TRANSMITTABLE_SCHEMA)


# def register_action(name, type_, schema):
#     validator = templatize(schema).extend(BASE_REMOTE_TRANSMITTER_SCHEMA)
#     registerer = automation.register_action(
#         f"remote_transmitter.transmit_{name}", type_, validator
#     )

#     def decorator(func):
#         async def new_func(config, action_id, template_arg, args):
#             var = cg.new_Pvariable(action_id, template_arg)
#             await register_transmittable(var, config)
#             if CONF_REPEAT in config:
#                 conf = config[CONF_REPEAT]
#                 template_ = await cg.templatable(conf[CONF_TIMES], args, cg.uint32)
#                 cg.add(var.set_send_times(template_))
#                 template_ = await cg.templatable(conf[CONF_WAIT_TIME], args, cg.uint32)
#                 cg.add(var.set_send_wait(template_))
#             await coroutine(func)(var, config, args)
#             return var

#         return registerer(new_func)

#     return decorator


# def declare_protocol(name):
#     data = ns.struct(f"{name}Data")
#     # binary_sensor_ = ns.class_(f"{name}BinarySensor", RemoteReceiverBinarySensorBase)
#     trigger = ns.class_(f"{name}Trigger", RemoteReceiverTrigger)
#     # action = ns.class_(f"{name}Action", RemoteTransmitterActionBase)
#     dumper = ns.class_(f"{name}Dumper", RemoteTransmitterDumper)
#     return data, trigger, dumper


# BINARY_SENSOR_REGISTRY = Registry(
#     binary_sensor.binary_sensor_schema().extend(
#         {
#             cv.GenerateID(CONF_RECEIVER_ID): cv.use_id(RemoteReceiverBase),
#         }
#     )
# )
# validate_binary_sensor = cv.validate_registry_entry(
#     "remote receiver", BINARY_SENSOR_REGISTRY
# )
TRIGGER_REGISTRY = SimpleRegistry()
DUMPER_REGISTRY = Registry(
    {
        cv.Optional(CONF_RECEIVER_ID): cv.invalid(
            "This has been removed in ESPHome 1.20.0 and the dumper attaches directly to the parent receiver."
        ),
    }
)


def validate_dumpers(value):
    if isinstance(value, str) and value.lower() == "all":
        return validate_dumpers(list(DUMPER_REGISTRY.keys()))
    return cv.validate_registry("dumper", DUMPER_REGISTRY)(value)


def validate_triggers(base_schema):
    assert isinstance(base_schema, cv.Schema)

    @schema_extractor("triggers")
    def validator(config):
        added_keys = {}
        for key, (_, valid) in TRIGGER_REGISTRY.items():
            added_keys[cv.Optional(key)] = valid
        new_schema = base_schema.extend(added_keys)

        if config == SCHEMA_EXTRACT:
            return new_schema
        return new_schema(config)

    return validator


# async def build_binary_sensor(full_config):
#     registry_entry, config = cg.extract_registry_entry_config(
#         BINARY_SENSOR_REGISTRY, full_config
#     )
#     type_id = full_config[CONF_TYPE_ID]
#     builder = registry_entry.coroutine_fun
#     var = cg.new_Pvariable(type_id)
#     await cg.register_component(var, full_config)
#     await register_listener(var, full_config)
#     await builder(var, config)
#     return var


async def build_triggers(full_config):
    triggers = []
    for key in TRIGGER_REGISTRY:
        for config in full_config.get(key, []):
            func = TRIGGER_REGISTRY[key][0]
            triggers.append(await func(config))
    return triggers


async def build_dumpers(config):
    dumpers = []
    for conf in config:
        dumper = await cg.build_registry_entry(DUMPER_REGISTRY, conf)
        dumpers.append(dumper)
    return dumpers



# RC Switch Raw
# RC_SWITCH_TIMING_SCHEMA = cv.All([cv.uint8_t], cv.Length(min=2, max=2))

# RC_SWITCH_PROTOCOL_SCHEMA = cv.Any(
#     cv.int_range(min=1, max=8),
#     cv.Schema(
#         {
#             cv.Required(CONF_PULSE_LENGTH): cv.uint32_t,
#             cv.Optional(CONF_SYNC, default=[1, 31]): RC_SWITCH_TIMING_SCHEMA,
#             cv.Optional(CONF_ZERO, default=[1, 3]): RC_SWITCH_TIMING_SCHEMA,
#             cv.Optional(CONF_ONE, default=[3, 1]): RC_SWITCH_TIMING_SCHEMA,
#             cv.Optional(CONF_INVERTED, default=False): cv.boolean,
#         }
#     ),
# )





# def build_rc_switch_protocol(config):
#     if isinstance(config, int):
#         return rc_switch_protocols[config]
#     pl = config[CONF_PULSE_LENGTH]
#     return RCSwitchBase(
#         config[CONF_SYNC][0] * pl,
#         config[CONF_SYNC][1] * pl,
#         config[CONF_ZERO][0] * pl,
#         config[CONF_ZERO][1] * pl,
#         config[CONF_ONE][0] * pl,
#         config[CONF_ONE][1] * pl,
#         config[CONF_INVERTED],
#     )



# RC_SWITCH_RAW_SCHEMA = cv.Schema(
#     {
#         cv.Required(CONF_CODE): validate_rc_switch_raw_code,
#         cv.Optional(CONF_PROTOCOL, default=1): RC_SWITCH_PROTOCOL_SCHEMA,
#     }
# )
# RC_SWITCH_TYPE_A_SCHEMA = cv.Schema(
#     {
#         cv.Required(CONF_GROUP): cv.All(
#             validate_rc_switch_code, cv.Length(min=5, max=5)
#         ),
#         cv.Required(CONF_DEVICE): cv.All(
#             validate_rc_switch_code, cv.Length(min=5, max=5)
#         ),
#         cv.Required(CONF_STATE): cv.boolean,
#         cv.Optional(CONF_PROTOCOL, default=1): RC_SWITCH_PROTOCOL_SCHEMA,
#     }
# )
# RC_SWITCH_TYPE_B_SCHEMA = cv.Schema(
#     {
#         cv.Required(CONF_ADDRESS): cv.int_range(min=1, max=4),
#         cv.Required(CONF_CHANNEL): cv.int_range(min=1, max=4),
#         cv.Required(CONF_STATE): cv.boolean,
#         cv.Optional(CONF_PROTOCOL, default=1): RC_SWITCH_PROTOCOL_SCHEMA,
#     }
# )
# RC_SWITCH_TYPE_C_SCHEMA = cv.Schema(
#     {
#         cv.Required(CONF_FAMILY): cv.one_of(
#             "a",
#             "b",
#             "c",
#             "d",
#             "e",
#             "f",
#             "g",
#             "h",
#             "i",
#             "j",
#             "k",
#             "l",
#             "m",
#             "n",
#             "o",
#             "p",
#             lower=True,
#         ),
#         cv.Required(CONF_GROUP): cv.int_range(min=1, max=4),
#         cv.Required(CONF_DEVICE): cv.int_range(min=1, max=4),
#         cv.Required(CONF_STATE): cv.boolean,
#         cv.Optional(CONF_PROTOCOL, default=1): RC_SWITCH_PROTOCOL_SCHEMA,
#     }
# )
# RC_SWITCH_TYPE_D_SCHEMA = cv.Schema(
#     {
#         cv.Required(CONF_GROUP): cv.one_of("a", "b", "c", "d", lower=True),
#         cv.Required(CONF_DEVICE): cv.int_range(min=1, max=3),
#         cv.Required(CONF_STATE): cv.boolean,
#         cv.Optional(CONF_PROTOCOL, default=1): RC_SWITCH_PROTOCOL_SCHEMA,
#     }
# )
# RC_SWITCH_TRANSMITTER = cv.Schema(
#     {
#         cv.Optional(CONF_REPEAT, default={CONF_TIMES: 5}): cv.Schema(
#             {
#                 cv.Required(CONF_TIMES): cv.templatable(cv.positive_int),
#                 cv.Optional(CONF_WAIT_TIME, default="0us"): cv.templatable(
#                     cv.positive_time_period_microseconds
#                 ),
#             }
#         ),
#     }
# )

# rc_switch_protocols = ns.RC_SWITCH_PROTOCOLS
# RCSwitchData = ns.struct("RCSwitchData")
# RCSwitchBase = ns.class_("RCSwitchBase")
# RCSwitchTrigger = ns.class_("RCSwitchTrigger", RemoteReceiverTrigger)
# RCSwitchDumper = ns.class_("RCSwitchDumper", RemoteTransmitterDumper)
# RCSwitchRawAction = ns.class_("RCSwitchRawAction", RemoteTransmitterActionBase)
# RCSwitchTypeAAction = ns.class_("RCSwitchTypeAAction", RemoteTransmitterActionBase)
# RCSwitchTypeBAction = ns.class_("RCSwitchTypeBAction", RemoteTransmitterActionBase)
# RCSwitchTypeCAction = ns.class_("RCSwitchTypeCAction", RemoteTransmitterActionBase)
# RCSwitchTypeDAction = ns.class_("RCSwitchTypeDAction", RemoteTransmitterActionBase)
# RCSwitchRawReceiver = ns.class_("RCSwitchRawReceiver", RemoteReceiverBinarySensorBase)


RCSwitchCustomTrigger = ns.class_("RCSwitchCustomTrigger", RemoteReceiverTrigger)

RCSwitchCustomDumper = ns.class_("RCSwitchCustomDumper", RemoteTransmitterDumper)

@register_trigger("rc_switch_custom", RCSwitchCustomTrigger, RCSwitchData)
def rc_switch_custom_trigger(var, config):
    pass

@register_dumper("rc_switch_custom", RCSwitchCustomDumper)
def rc_switch_dumper(var, config):
    pass

