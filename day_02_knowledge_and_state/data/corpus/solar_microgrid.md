# Campus Solar Microgrid — Operating Notes

## Purpose

The campus microgrid combines rooftop solar photovoltaic generation, a battery energy storage system, controllable loads, and a grid connection. Its primary goals are to reduce peak grid demand, preserve critical services during short outages, and increase the fraction of locally consumed renewable energy.

## Operating modes

In grid-connected mode, the utility grid establishes voltage and frequency. The microgrid controller schedules battery charging when solar generation exceeds campus demand and may discharge the battery during the evening peak. Export to the utility is disabled in the teaching installation.

In islanded mode, the battery inverter establishes the local voltage and frequency. Only the critical-load panel remains energized. Laboratory air-conditioning and vehicle charging are disconnected automatically to prevent the islanded system from being overloaded.

## Transition conditions

The controller opens the point-of-common-coupling breaker after detecting utility voltage or frequency outside the permitted range for the configured protection interval. Before reconnecting, it verifies that utility voltage, frequency, and phase remain within synchronization limits for five continuous minutes.

## Load priorities

Priority 1 loads include emergency lighting, network equipment, fire-alarm equipment, and the medical room refrigerator. Priority 2 includes selected laboratory instruments. Priority 3 includes comfort cooling, water heating, and vehicle charging. Lower-priority loads are shed first.

## Limitation

The teaching microgrid is designed for short-duration resilience, not indefinite backup. Available islanding time depends on battery state of charge, critical-load demand, temperature, and battery power limits.

