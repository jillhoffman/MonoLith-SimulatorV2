# Monolith Simulator V2 — Model Documentation

This repository implements a physics-based techno-economic model for a lithium extraction electrochemical plant.  
The system is structured into modular components:

- `electrochem.py` → electrochemical performance model
- `mass_balance.py` → process flow and separations
- `economics.py` → CAPEX/OPEX and costing
- `results.py` → full integrated plant simulation
- `inputs.py` → unified parameter schema
- `scenarios.py` → preset operating cases

---
# Monolith Simulator V2 — Full Model Documentation

This repository implements a techno-economic model for an electrochemical lithium extraction process.

It is organized into modular physics, process, and economic components, all integrated through `results.py` and visualized in a Streamlit/Shiny-style application.
---

# Creating Environment and Running App

### 1. Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
### 2. Create conda env

```bash
conda env create -f environment.yml
conda activate monolith
```

### 3. Run app
```bash
shiny run shiny_app.py

```

---
# Electrochemistry Model

---

## Total Current

$$
I_{total} = j \cdot A_{electrode} \cdot N_{active}
$$


## Active Stacks

$$
N_{active} = \max(1, \text{round}(N_{installed} \cdot f_{active}))
$$


## Cell Voltage

$$
V_{cell} = V_{thermo} + V_{ohmic} + V_{activation} + V_{concentration}
$$


## Ohmic Loss

$$
V_{ohmic} = \frac{I_{total} \cdot ASR}{A_{electrode}}
$$


## Activation Loss

$$
V_{activation} = k \ln(\max(j, 1))
$$


## Concentration Loss

$$
V_{concentration} = \frac{0.05}{1 - \frac{j}{j_{lim}}}
$$


## Lithium Production

$$
\dot{n}_{Li} = \frac{I_{total} \cdot FE}{F}
$$


## Power

$$
P = \frac{I_{total} \cdot V_{cell}}{1000}
$$

---

# Mass Balance Model

---

## Stream Conversion

$$
\dot{m} = Q \cdot C
$$

## Pretreatment

$$
Li_{pt} = Li \cdot R_{Li}
$$

$$
Mg_{pt} = Mg (1 - R_{Mg})
$$

## Stack Recovery

$$
Li_{product} = Li \cdot R_{stack}
$$

$$
Li_{recycle} = Li (1 - R_{stack})
$$

## Polishing

$$
Li_{polished} = Li_{product} \cdot R_{polishing}
$$


## Final Product

$$
Li_{final} = Li_{polished} \cdot R_{product}
$$

## Overall Recovery

$$
R =
R_{pretreatment} \cdot R_{stack} \cdot R_{polishing} \cdot R_{product}
$$

---
# Economics Model

---

## Annual Production

$$
t/y = \frac{kg/h \cdot 8760 \cdot uptime}{1000}
$$

## Electricity Cost

$$
Cost_{elec} =
\frac{P \cdot 8760 \cdot uptime}{1000} \cdot price
$$

## Stack Replacement Cost

$$
Cost_{stack} = N_{stacks} \cdot C_{stack}
$$

## CAPEX Scaling

$$
CAPEX = C_0 \left(\frac{tpy}{tpy_{ref}}\right)^{\alpha}
$$

## Total OPEX

$$
OPEX = Cost_{elec} + Cost_{stack} + Cost_{fixed}
$$


## OPEX per Ton

$$
OPEX/t = \frac{OPEX}{t/y}
$$

---

# Full Equation Library

---

## Energy Intensity

$$
SEC = \frac{P}{\dot{m}}
$$

## Power

$$
P = I V
$$

## Current

$$
I = j A N
$$

## Recovery

$$
R =
R_{pt} R_{stack} R_{polish} R_{product}
$$

## Mass Balance Error

$$
Error = Li_{in} - Li_{out}
$$




