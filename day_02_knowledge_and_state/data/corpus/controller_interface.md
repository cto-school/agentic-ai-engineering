# Microgrid Controller — Interface Reference

## Telemetry

The controller exposes read-only telemetry for solar power, battery power, battery state of charge, grid import, critical-load demand, operating mode, and active alarms. Power values use kilowatts and state of charge uses percentage.

## Commands

The teaching API supports `set_battery_power_limit`, `request_island_mode`, and `acknowledge_alarm`. A positive battery power limit permits discharge; a negative value permits charging. The permitted magnitude is restricted by the current battery-management-system limits.

`request_island_mode` does not immediately open the grid breaker. It starts a validation sequence that checks battery state of charge, inverter readiness, protection status, and estimated critical-load demand. The controller rejects the request if any precondition fails.

## Authorization

Telemetry requires the `viewer` role. Changing a power limit requires the `operator` role. Requesting island mode requires the `operator` role and a second human confirmation. Protection settings cannot be changed through the teaching API.

## Errors

Errors use a structured object containing `code`, `message`, and `retryable`. Validation failures are not retryable until the input or system condition changes. Temporary communication failures may be retried twice with a delay. Repeating a rejected operational command without changing conditions is prohibited.

## Audit trail

Every command attempt records the user identifier, timestamp, requested action, validated arguments, authorization result, approval result, and final execution status. Read-only telemetry queries are aggregated rather than stored individually.

