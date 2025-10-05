# Mathematical Modelling — Network Flow Optimisation (Transportation Problem)

## Project Overview
This project develops and analyses a mathematical optimisation model for a UK paint manufacturer to determine the most cost-efficient transportation plan across its supply network. The company operates **two factories** (Bristol and Leeds), **three regional warehouses** (London, Birmingham, Glasgow), and **five wholesalers** distributed nationwide.  
The goal is to **minimise total weekly transport cost** while meeting all customer demand and respecting factory and warehouse capacity limits.

---

## Business Context
Paint produced at the factories can either be shipped **directly to wholesalers** or **routed through one of the warehouses** before final delivery. Each possible route has an associated transport cost (£ per ton), and some routes are infeasible due to distance or logistics.  

The company seeks to:
1. Establish the **minimum-cost transport plan** using all three warehouses (Question 1a).  
2. Examine how **capacity changes** at factories or warehouses affect overall cost (Question 1b).  
3. Evaluate **strategic options** to reduce fixed overheads by closing or sub-letting a warehouse, using a **Mixed Integer Linear Programming (MILP)** model (Question 1c).

---

## Data Summary

| Supplier  | **London** | **Birmingham** | **Glasgow** | **Wholesaler 1** | **Wholesaler 2** | **Wholesaler 3** | **Wholesaler 4** | **Wholesaler 5** |
|:-----------|-----------:|---------------:|-------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|
| **Bristol** | 25 | 23 | – | 80 | – | 90 | 100 | 86 |
| **Leeds**   | 30 | 27 | 30 | – | 70 | 54 | – | 100 |
| **London**  | – | – | – | 37 | 31 | – | 40 | 44 |
| **Birmingham** | – | – | – | 36 | 40 | 43 | 40 | 46 |
| **Glasgow** | – | – | – | 45 | 42 | 30 | – | 36 |

All numbers represent **transport cost (£ per ton)**.  
A dash (–) indicates that a route is **logistically infeasible**.  
To preserve model completeness, infeasible routes are assigned a **prohibitive cost (£ 500 per ton)** in the optimisation, discouraging the solver from selecting them while maintaining a fully defined cost matrix.

---

## Key Model Parameters
| Parameter | Description | Value |
|:-----------|:-------------|:------|
| Factory Capacities | Bristol = 40 000 t/week, Leeds = 50 000 t/week | |
| Warehouse Capacities | London = 20 000 t, Birmingham = 15 000 t, Glasgow = 12 000 t | |
| Wholesaler Demand | W1 = 15 000 t, W2 = 20 000 t, W3 = 13 000 t, W4 = 14 000 t, W5 = 16 000 t | |

---

## Model Type
- **Problem 1 / 2:** Linear Programming (LP)  
  - Continuous shipment variables  
  - Objective: minimise total transport cost  
  - Constraints: supply ≤ capacity, demand ≥ requirement, non-negativity  
- **Problem 3:** Mixed Integer Linear Programming (MILP)  
  - Adds binary variables (`Yj = 1` if warehouse *j* open, else 0)  
  - Logical constraint `Xij ≤ M × Yj` ties route usage to warehouse status  
  - Enables evaluation of warehouse closure and sub-letting options  

---

## Analytical Workflow
1. **Base Model (LP – Problem 1):**  
   Determine the minimum-cost transport plan using all three warehouses.  
   → *Optimal weekly cost ≈ £ 4.94 million.*

2. **Capacity Sensitivity (LP – Problem 2):**  
   Re-solve the model under incremental capacity changes (±1 ton) to identify cost sensitivity and marginal values of capacity.

3. **Warehouse Closure Scenario (MILP – Problem 3):**  
   Introduce binary variables to test scenarios where only two warehouses may remain open.  
   The solver recommends closing **Glasgow**, resulting in a new minimum weekly cost of **£ 5.19 million** — a £ 254 000 increase from the optimal baseline.  
   Further comparison shows that if **Birmingham** were closed instead and sub-let at £ 21 000 per 1000 tons per week (total £ 315 000), the net transport cost after rental earnings would reduce to **£ 4.93 million**, making it the more economical decision.

---

## Outcome Summary
| Scenario | Model Type | Weekly Cost (£) | Δ vs Baseline | Decision |
|:----------|:------------|----------------:|---------------:|:----------|
| All warehouses open | LP | 4 937 000 | – | Optimal base plan |
| Glasgow closed | MILP | 5 191 000 | + 254 000 | Higher cost |
| Birmingham closed (with rent) | MILP + Economic Adjustment | 4 925 000 | − 12 000 | Recommended |

---

## Tools & Dependencies
- **Python 3.11**  
- **PuLP 2.8+** (CBC solver)  
- **Pandas / NumPy** (data handling and output formatting)  
- **Stata 17** and **Excel Solver** used initially for model validation  

---

## Deliverables
1. **`paint_transport_LP.py`** — linear programming model (Question 1a)  
2. **`paint_transport_MILP.py`** — mixed-integer model with warehouse closure logic (Question 1c)  
3. **README.md** — project documentation and summary report  

---

## Business Insight
This modelling framework provides a reusable optimisation tool for logistics planning, allowing management to:
- Minimise distribution cost under changing capacity and demand.  
- Quantify the cost impact of closing or renting warehouse capacity.  
- Support strategic decisions with data-driven financial justification.
