From the 9/17 call ([corrected transcript]({{TRANSCRIPT}})). Before Bartosz arrives we want to know what computer control and integration the rePowder supports, so the lab computer plan (#114, #122, #154) covers it. Nothing on this is in the repo yet; the manual excerpts in #126 are safety and procedures only.

What's public: the system ships with integrated control software for process control, monitoring, and data recording; process data is accessible through the system software; cameras and O2 sensors are supported add-ons "after consulting AMAZEMET" ([FAQ](https://www.amazemet.com/faq/)); newer units have an Advanced Control Cabinet with an industrial PLC and GPU and an API for remote process control and monitoring ([Metal AM](https://www.metal-am.com/amazemet-adds-ai-automation-to-repowder-atomisation/)).

Questions for Bartosz:
- Is the control software on the machine (PLC/HMI) or on a separate PC? If a PC: Windows or Linux, x86 only or is ARM (Pi 5) OK, and is the PC supplied?
- How does a PC talk to the machine: Ethernet, USB, serial? Any API (REST, OPC UA, Modbus)? Does our unit have the Advanced Control Cabinet, or is that a retrofit?
- Process data: format, export, can we pull it programmatically?
- Remote monitoring or control: supported, and what network access does the machine need?

I'll attach the manuals (O&MM_rePowder_04_2023.pdf, the Facility Guide, TechDoku) in a follow-up comment.
<!-- if-trigger -->

@claude compile what's public on rePowder control, software, and API (AMAZEMET site and FAQ, the Metal AM and Siemens Xcelerator articles) into a short sourced table, and tighten the question list above. Ultra brief.
<!-- end-if-trigger -->

<!-- queue:2026-09-17-new-software -->
