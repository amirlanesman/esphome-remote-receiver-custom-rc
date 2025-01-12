#include "rc_switch_custom_protocol.h"
#include "esphome/core/log.h"

namespace esphome {
namespace remote_base {

static const char *const TAG = "remote.rc_switch_custom";

const RCSwitchBase RC_SWITCH_CUSTOM_PROTOCOLS[2] = {RCSwitchBase(0, 0, 0, 0, 0, 0, false),
                                             RCSwitchBase(9990, 333, 333, 666, 666, 333, true)};


optional<RCSwitchData> RCSwitchCustom::decode(RemoteReceiveData &src) const {
  RCSwitchData out;
  uint8_t out_nbits;
  for (uint8_t i = 1; i <= 1; i++) {
    src.reset();
    const RCSwitchBase *protocol = &RC_SWITCH_CUSTOM_PROTOCOLS[i];
    if (protocol->decode(src, &out.code, &out_nbits) && out_nbits >= 3) {
      out.protocol = i;
      return out;
    }
  }
  return {};
}

bool RCSwitchCustomDumper::dump(RemoteReceiveData src) {
  for (uint8_t i = 1; i <= 1; i++) {
    src.reset();
    uint64_t out_data;
    uint8_t out_nbits;
    const RCSwitchBase *protocol = &RC_SWITCH_CUSTOM_PROTOCOLS[i];
    if (protocol->decode(src, &out_data, &out_nbits) && out_nbits >= 3) {
      char buffer[65];
      for (uint8_t j = 0; j < out_nbits; j++)
        buffer[j] = (out_data & ((uint64_t) 1 << (out_nbits - j - 1))) ? '1' : '0';

      buffer[out_nbits] = '\0';
      ESP_LOGI(TAG, "Received RCSwitch Custom Raw: protocol=%u data='%s'", i, buffer);

      // only send first decoded protocol
      return true;
    }
  }
  return false;
}

}  // namespace remote_base
}  // namespace esphome
