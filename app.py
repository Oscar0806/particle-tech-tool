import streamlit as st
import plotly.graph_objects as go
import numpy as np
from particle_engine import (generate_sieve_data, fit_rosin_rammler,
    fit_ggs, rosin_rammler, gates_gaudin_schuhmann, bond_energy,
    simulate_crusher, WORK_INDICES)
 
st.set_page_config(page_title="Particle Technology", page_icon="⚙️", layout="wide")
st.title("⚙️ Particle Size Analysis & Crusher Simulation")
st.markdown("**Rosin-Rammler, GGS, Bond's Law – Particle Technology & Recycling**")
st.divider()
 
st.sidebar.header("📊 Sieve Analysis")
input_mode = st.sidebar.selectbox("Data source", ["Generate sample","Enter manually"])
if input_mode == "Generate sample":
    d50 = st.sidebar.slider("Median size d50 (mm)", 0.1, 50.0, 5.0, 0.5)
    spread = st.sidebar.slider("Distribution spread", 0.3, 2.0, 0.8, 0.1)
    sizes, passing = generate_sieve_data(d50, spread)
else:
    sizes_str = st.sidebar.text_area("Sieve sizes (mm)", "0.5,1.0,2.0,4.0,8.0,16.0,31.5,63.0")
    passing_str = st.sidebar.text_area("Cum % passing", "5,12,28,52,78,92,98,100")
    sizes = np.array([float(x) for x in sizes_str.split(",")])
    passing = np.array([float(x) for x in passing_str.split(",")])
 
st.sidebar.header("🔨 Crusher")
crusher = st.sidebar.selectbox("Crusher type", ["Jaw Crusher","Cone Crusher","Ball Mill"])
material = st.sidebar.selectbox("Material", list(WORK_INDICES.keys()))
 
rr = fit_rosin_rammler(sizes, passing)
ggs = fit_ggs(sizes, passing)
 
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("d63 (RR)", f"{rr['d63']:.2f} mm")
with c2: st.metric("n (RR)", f"{rr['n']:.2f}")
with c3: st.metric("d_max (GGS)", f"{ggs['d_max']:.2f} mm")
with c4: st.metric("m (GGS)", f"{ggs['m']:.2f}")
with c5: st.metric("Wi", f"{WORK_INDICES[material]} kWh/t")
st.divider()
 
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Particle Size Distribution")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sizes,y=passing,mode="markers",name="Measured (sieve)",
        marker=dict(size=8,color="#2C3E50")))
    d_fine = np.linspace(min(sizes)*0.5, max(sizes)*1.5, 200)
    fig.add_trace(go.Scatter(x=d_fine,y=rosin_rammler(d_fine,rr["d63"],rr["n"]),
        mode="lines",name=f"Rosin-Rammler (d63={rr['d63']:.2f}, n={rr['n']:.2f})",
        line=dict(color="#E74C3C",width=2)))
    fig.add_trace(go.Scatter(x=d_fine,y=gates_gaudin_schuhmann(d_fine,ggs["d_max"],ggs["m"]),
        mode="lines",name=f"GGS (d_max={ggs['d_max']:.2f}, m={ggs['m']:.2f})",
        line=dict(color="#3498DB",width=2,dash="dash")))
    fig.update_layout(xaxis_title="Particle size (mm)",yaxis_title="Cum % passing",
        xaxis_type="log",height=400,template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
 
with col2:
    st.subheader("🔨 Feed vs Product")
    result = simulate_crusher(sizes, passing, crusher)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=sizes,y=passing,mode="lines+markers",name="Feed",
        line=dict(color="#2C3E50",width=2)))
    fig2.add_trace(go.Scatter(x=result["product_sizes"],y=result["product_passing"],
        mode="lines+markers",name=f"Product ({crusher})",
        line=dict(color="#27AE60",width=2)))
    fig2.update_layout(xaxis_title="Particle size (mm)",yaxis_title="Cum % passing",
        xaxis_type="log",height=400,template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
 
st.subheader("⚡ Bond's Comminution Energy")
col3, col4 = st.columns(2)
with col3:
    F80 = rr["d63"] * 1000
    P80_range = np.linspace(50, F80*0.9, 50)
    Wi = WORK_INDICES[material]
    energies = [bond_energy(Wi, F80, p80) for p80 in P80_range]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=P80_range/1000,y=energies,mode="lines",
        name=f"{material} (Wi={Wi})",line=dict(color="#9B59B6",width=2),
        fill="tozeroy",fillcolor="rgba(155,89,182,0.1)"))
    fig3.update_layout(xaxis_title="Product P80 (mm)",yaxis_title="Energy (kWh/ton)",
        height=350,template="plotly_white",title=f"Comminution Energy ({material})")
    st.plotly_chart(fig3, use_container_width=True)
with col4:
    st.markdown("**Crusher Performance**")
    st.markdown(f"- Crusher: **{crusher}**")
    st.markdown(f"- Material: **{material}** (Wi={Wi} kWh/t)")
    st.markdown(f"- Reduction ratio: **{result['reduction_ratio']}:1**")
    st.markdown(f"- Feed d63: **{rr['d63']:.2f} mm**")
    st.markdown(f"- Product d63: **{result['d63_product']:.3f} mm**")
    P80_prod = result["d63_product"]*1000
    E = bond_energy(Wi, F80, max(P80_prod,10))
    st.markdown(f"- Energy: **{E:.2f} kWh/ton**")
    st.markdown(f"- Power at 100 t/h: **{E*100:.0f} kW**")
 
st.divider()
st.caption("Particle Technology | Recycling & Process Engineering | Oscar Vincent Dbritto ")
