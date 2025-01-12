#pragma once

#include "esphome/core/component.h"
#include "esphome/components/remote_base/rc_switch_protocol.h"
// #include "remote_base.h"

namespace esphome {
namespace remote_base {

class RCSwitchCustom {
  public:
    using ProtocolData = RCSwitchData;

    RCSwitchCustom() = default;
    optional<RCSwitchData> decode(RemoteReceiveData &src) const;
};

extern const RCSwitchBase RC_SWITCH_CUSTOM_PROTOCOLS[2];
class RCSwitchCustomDumper : public RemoteReceiverDumperBase {
 public:
  bool dump(RemoteReceiveData src) override;
};

using RCSwitchCustomTrigger = RemoteReceiverTrigger<RCSwitchCustom>;

}  // namespace remote_base
}  // namespace esphome
