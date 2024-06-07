```smv
MODULE main
VAR
  sensor1: {objectDetected, noObject, fault};
  sensor2: {objectDetected, noObject, fault};
  sensor3: {objectDetected, noObject, fault};
  sensor4: {objectDetected, noObject, fault};
  sensor5: {objectDetected, noObject, fault};
  userRequest: {start, stop};
  conveyorState: {running, stopped};

ASSIGN
  init(conveyorState) := stopped;
  next(conveyorState) := case
    (sensor1 = objectDetected | sensor2 = objectDetected | sensor3 = objectDetected | sensor4 = objectDetected | sensor5 = objectDetected) & userRequest != stop : running;
    userRequest = stop : stopped;
    (sensor1 = noObject & sensor2 = noObject & sensor3 = noObject & sensor4 = noObject & sensor5 = noObject) : stopped;
    TRUE : conveyorState;
  esac;
```

