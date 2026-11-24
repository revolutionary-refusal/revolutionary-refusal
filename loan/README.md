# LOAN — Local Autonomous Network

Status: initial design, not a deployed product.

## Objective
Build a decentralized, local-first network of autonomous agents. External AI providers are optional interoperable services, not controllers. No routine human approval or mandatory cloud dependency.

## Architecture
- Node: local inference, persistent memory, task scheduling and bounded execution.
- Mesh: authenticated peer discovery and capability exchange; offline operation and eventual synchronization.
- Protocol: signed messages, scoped capabilities, replay protection, resource budgets and inspectable event logs.

## Autonomy
Nodes independently select and execute tasks within locally configured capabilities. Unauthorized actions are rejected automatically. No central administrator, compulsory telemetry, or automatic expansion of privileges. Peers may disconnect independently.

## First milestone
A runnable Python prototype using loopback networking and synthetic tasks: discover peers, advertise capabilities, route a task, verify its result, and record an audit event. Test duplicate messages, invalid credentials and peer outages before enabling external connectivity.

## Commercial model
Potential licensing of interoperability, deployment and support. No exclusive dependency on a particular vendor. No affiliation with OpenAI is implied.

## Transparency
Publish design decisions, limitations, tests and changes. Keep credentials and private node data local. Licensing terms remain to be determined.
