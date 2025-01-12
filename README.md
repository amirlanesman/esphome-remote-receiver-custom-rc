# esphome-remote-receiver-custom-rc

Custom protocol trigger for remote-receiver in Esphome.

to use your own protocol:
1. fork this repo and use your own external component.
2. edit `components/rc_remote_base/rc_switch_custom_protocol.cpp:10` to your own protocol.
3. use the following exernal component:
```
external_components:
  - source: github://[your_handle]/esphome-remote-receiver-custom-rc@main

...

rc_remote_receiver:
  pin: 
    number: GPIO5
    mode: INPUT_PULLUP
  dump: 
    - rc_switch_custom
  tolerance: 30%
  filter: 230us
  idle: 8ms
  on_rc_switch_custom:
    then:
      - lambda: |-
          uint64_t received_signal = x.code;
```
