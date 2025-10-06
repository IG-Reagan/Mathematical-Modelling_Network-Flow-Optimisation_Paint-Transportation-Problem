"""
paint_transport_MILP.py
Author: Giwa Iziomo

MILP that decides which two warehouses (London, Birmingham, Glasgow) to keep open.
Includes: factory→warehouse, factory→wholesaler, and warehouse→wholesaler flows.
Variant objective subtracts rental income if Birmingham is closed.
"""
# Install PuLP
!pip install pulp

# Import PuLP
import pulp

# -----------------------------
# 1. Sets
# -----------------------------

factories = ["Bristol", "Leeds"]
warehouses = ["London", "Birmingham", "Glasgow"]
wholesalers = ["Wholesaler 1", "Wholesaler 2", "Wholesaler 3", "Wholesaler 4", "Wholesaler 5"]

# -----------------------------
# 2. Parameters
# -----------------------------

# Factory -> Warehouse costs (£/t)
fw_cost = {
    ("Bristol", "London"): 25, ("Bristol", "Birmingham"): 23, ("Bristol", "Glasgow"): 500,
    ("Leeds", "London"): 30, ("Leeds", "Birmingham"): 27, ("Leeds", "Glasgow"): 30,
}

# Factory -> Wholesaler direct costs (£/t)  (500 = prohibitive/infeasible)
fh_cost = {
    ("Bristol", "Wholesaler 1"): 80, ("Bristol", "Wholesaler 2"): 500, ("Bristol", "Wholesaler 3"): 90,
    ("Bristol", "Wholesaler 4"): 100, ("Bristol", "Wholesaler 5"): 86,
    ("Leeds", "Wholesaler 1"): 500, ("Leeds", "Wholesaler 2"): 70, ("Leeds", "Wholesaler 3"): 54,
    ("Leeds", "Wholesaler 4"): 500, ("Leeds", "Wholesaler 5"): 100,
}

# Warehouse -> Wholesaler costs (£/t)
wh_cost = {
    ("London", "Wholesaler 1"): 37, ("London", "Wholesaler 2"): 31,
    ("London", "Wholesaler 3"): 500, ("London", "Wholesaler 4"): 40, ("London", "Wholesaler 5"): 44,
    ("Birmingham", "Wholesaler 1"): 36, ("Birmingham", "Wholesaler 2"): 40,
    ("Birmingham", "Wholesaler 3"): 43, ("Birmingham", "Wholesaler 4"): 40, ("Birmingham", "Wholesaler 5"): 46,
    ("Glasgow", "Wholesaler 1"): 45, ("Glasgow", "Wholesaler 2"): 42,
    ("Glasgow", "Wholesaler 3"): 30, ("Glasgow", "Wholesaler 4"): 500, ("Glasgow", "Wholesaler 5"): 36,
}

# Supplies (tons/week)
supply = {"Bristol": 40000, "Leeds": 50000}

# Warehouse capacities (tons/week)
capacity = {"London": 20000, "Birmingham": 15000, "Glasgow": 12000}

# Demands (tons/week)
demand = {"Wholesaler 1": 15000, "Wholesaler 2": 20000, "Wholesaler 3": 13000,
          "Wholesaler 4": 14000, "Wholesaler 5": 16000}

M = 10**6  # Big-M for safety

# -----------------------------
# 3. MILP: transport cost only
# -----------------------------

model = pulp.LpProblem("Paint_MILP_Choose_2_Warehouses", pulp.LpMinimize)

# Decision variables
x_fw = pulp.LpVariable.dicts("x_fw", fw_cost.keys(), lowBound=0)   # factory->warehouse
x_fh = pulp.LpVariable.dicts("x_fh", fh_cost.keys(), lowBound=0)   # factory->wholesaler
x_wh = pulp.LpVariable.dicts("x_wh", wh_cost.keys(), lowBound=0)   # warehouse->wholesaler
y = pulp.LpVariable.dicts("y", warehouses, lowBound=0, upBound=1, cat="Binary")  # open warehouse?

# Objective: minimise transport cost
model += (pulp.lpSum(fw_cost[k]*x_fw[k] for k in fw_cost) +
          pulp.lpSum(fh_cost[k]*x_fh[k] for k in fh_cost) +
          pulp.lpSum(wh_cost[k]*x_wh[k] for k in wh_cost))

# Factory supply
for i in factories:
    model += (pulp.lpSum(x_fw[(i,w)] for w in warehouses if (i,w) in fw_cost) +
              pulp.lpSum(x_fh[(i,h)] for h in wholesalers if (i,h) in fh_cost)
              <= supply[i]), f"supply_{i}"

# Warehouse balance & capacity (only if open)
for w in warehouses:
    inflow = pulp.lpSum(x_fw[(i,w)] for i in factories if (i,w) in fw_cost)
    outflow = pulp.lpSum(x_wh[(w,h)] for h in wholesalers if (w,h) in wh_cost)
    model += inflow == outflow, f"balance_{w}"
    model += outflow <= capacity[w] * y[w], f"capacity_{w}"
    model += outflow <= M * y[w], f"bigM_{w}"  # defensive

# Wholesaler demand
for h in wholesalers:
    model += (pulp.lpSum(x_fh[(i,h)] for i in factories if (i,h) in fh_cost) +
              pulp.lpSum(x_wh[(w,h)] for w in warehouses if (w,h) in wh_cost)
              >= demand[h]), f"demand_{h}"

# Exactly TWO warehouses open
model += pulp.lpSum(y[w] for w in warehouses) == 2, "two_warehouses_open"

# Solve
model.solve(pulp.PULP_CBC_CMD(msg=False))

print("Status (transport cost only):", pulp.LpStatus[model.status])
print(f"Minimum transport cost (2 warehouses open): £{pulp.value(model.objective):,.0f}")
print("Warehouses kept open:", [w for w in warehouses if y[w].value() > 0.5])

def print_flows():
    print("\nFactory -> Warehouse")
    for k,v in x_fw.items():
        if v.value() and v.value() > 1e-6:
            print(f"{k[0]} → {k[1]}: {v.value():,.0f} t @ £{fw_cost[k]}/t")
    print("\nFactory -> Wholesaler (direct)")
    for k,v in x_fh.items():
        if v.value() and v.value() > 1e-6:
            print(f"{k[0]} → {k[1]}: {v.value():,.0f} t @ £{fh_cost[k]}/t")
    print("\nWarehouse -> Wholesaler")
    for k,v in x_wh.items():
        if v.value() and v.value() > 1e-6:
            print(f"{k[0]} → {k[1]}: {v.value():,.0f} t @ £{wh_cost[k]}/t")
print_flows()

# -----------------------------
# 4. Variant: include rental income if Birmingham is closed
# -----------------------------

rent_per_week = 21_000       # £ per 1000 tons/week
bham_capacity = capacity["Birmingham"]  # 15,000 t
bham_rent_income = rent_per_week * (bham_capacity / 1000.0)  # £315,000/week

model_rent = pulp.LpProblem("Paint_MILP_With_Birmingham_Rent", pulp.LpMinimize)

x_fw2 = pulp.LpVariable.dicts("x_fw", fw_cost.keys(), lowBound=0)
x_fh2 = pulp.LpVariable.dicts("x_fh", fh_cost.keys(), lowBound=0)
x_wh2 = pulp.LpVariable.dicts("x_wh", wh_cost.keys(), lowBound=0)
y2 = pulp.LpVariable.dicts("y", warehouses, lowBound=0, upBound=1, cat="Binary")

# Objective: transport cost minus rental income if Birmingham is CLOSED
model_rent += (pulp.lpSum(fw_cost[k]*x_fw2[k] for k in fw_cost) +
               pulp.lpSum(fh_cost[k]*x_fh2[k] for k in fh_cost) +
               pulp.lpSum(wh_cost[k]*x_wh2[k] for k in wh_cost) -
               bham_rent_income * (1 - y2["Birmingham"]))

# Constraints (same structure)
for i in factories:
    model_rent += (pulp.lpSum(x_fw2[(i,w)] for w in warehouses if (i,w) in fw_cost) +
                   pulp.lpSum(x_fh2[(i,h)] for h in wholesalers if (i,h) in fh_cost)
                   <= supply[i])

for w in warehouses:
    inflow = pulp.lpSum(x_fw2[(i,w)] for i in factories if (i,w) in fw_cost)
    outflow = pulp.lpSum(x_wh2[(w,h)] for h in wholesalers if (w,h) in wh_cost)
    model_rent += inflow == outflow
    model_rent += outflow <= capacity[w] * y2[w]
    model_rent += outflow <= M * y2[w]

for h in wholesalers:
    model_rent += (pulp.lpSum(x_fh2[(i,h)] for i in factories if (i,h) in fh_cost) +
                   pulp.lpSum(x_wh2[(w,h)] for w in warehouses if (w,h) in wh_cost)
                   >= demand[h])

model_rent += pulp.lpSum(y2[w] for w in warehouses) == 2

model_rent.solve(pulp.PULP_CBC_CMD(msg=False))

print("\nStatus (with Birmingham rent):", pulp.LpStatus[model_rent.status])
print(f"Minimum net cost (transport – rent): £{pulp.value(model_rent.objective):,.0f}")
print("Warehouses kept open (with rent):", [w for w in warehouses if y2[w].value() > 0.5])
