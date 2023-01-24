# Entities
1. **Region**
    - coordinates
    - data_centers [DataCenter]
2. **Provider**
    - data_centers [DataCenter]
3. **DataCenter**
    - capacity
    - demand
    - allocation_cost
    - region [Region]
    - provider [Provider]
4. **User**
    - delay_sla
    - coordinates
    - application [Application]
5. **Application**
    - user [User]
    - services [Service]
6. **Service**
    - demand
    - application [Application]
    - data_center [DataCenter]
