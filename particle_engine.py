import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import lognorm
 
SIEVE_SIZES = [0.038,0.045,0.053,0.063,0.075,0.090,0.106,0.125,0.150,0.180,
    0.212,0.250,0.300,0.355,0.425,0.500,0.600,0.710,0.850,1.0,1.18,1.4,1.7,
    2.0,2.36,2.8,3.35,4.0,4.75,5.6,6.7,8.0,9.5,11.2,13.2,16.0,19.0,22.4,
    26.5,31.5,37.5,45.0,53.0,63.0,75.0,90.0]
 
def rosin_rammler(d, d63, n):
    """Rosin-Rammler: R(d) = 100*(1-exp(-(d/d63)^n))"""
    return 100 * (1 - np.exp(-(d / d63)**n))
 
def gates_gaudin_schuhmann(d, d_max, m):
    """GGS: R(d) = 100*(d/d_max)^m"""
    return np.minimum(100 * (d / d_max)**m, 100)
 
def fit_rosin_rammler(sizes, cum_passing):
    try:
        popt, _ = curve_fit(rosin_rammler, sizes, cum_passing,
            p0=[np.median(sizes), 1.5], bounds=([0.001,0.1],[1000,10]))
        return {"d63":round(popt[0],3), "n":round(popt[1],3)}
    except: return {"d63":np.median(sizes), "n":1.0}
 
def fit_ggs(sizes, cum_passing):
    try:
        popt, _ = curve_fit(gates_gaudin_schuhmann, sizes, cum_passing,
            p0=[max(sizes)*1.2, 0.8], bounds=([max(sizes)*0.5,0.1],[max(sizes)*5,5]))
        return {"d_max":round(popt[0],3), "m":round(popt[1],3)}
    except: return {"d_max":max(sizes)*1.5, "m":0.8}
 
def generate_sieve_data(d50, spread, n_sieves=12):
    np.random.seed(42)
    all_s = np.array(SIEVE_SIZES)
    idx = np.argmin(np.abs(all_s - d50))
    start = max(0, idx - n_sieves//2)
    end = min(len(all_s), start + n_sieves)
    sizes = all_s[start:end]
    mu = np.log(d50)
    cum_passing = lognorm.cdf(sizes, spread, scale=np.exp(mu)) * 100
    cum_passing += np.random.normal(0, 1.5, len(cum_passing))
    cum_passing = np.clip(np.sort(cum_passing), 0, 100)
    return sizes, cum_passing
 
def bond_energy(Wi, F80, P80):
    """Bond's Law: E = Wi*(10/sqrt(P80) - 10/sqrt(F80))"""
    return Wi * (10/np.sqrt(max(P80,1)) - 10/np.sqrt(max(F80,1)))
 
def simulate_crusher(feed_sizes, feed_passing, crusher_type, css_mm=None):
    rr_params = fit_rosin_rammler(feed_sizes, feed_passing)
    if crusher_type == "Jaw Crusher":
        rr, new_n = 6, rr_params["n"]*1.1
    elif crusher_type == "Cone Crusher":
        rr, new_n = 8, rr_params["n"]*1.2
    else:  # Ball Mill
        rr, new_n = 50, rr_params["n"]*0.9
    new_d63 = rr_params["d63"] / rr
    product_passing = rosin_rammler(feed_sizes, new_d63, new_n)
    return {"product_sizes":feed_sizes,"product_passing":product_passing,
            "d63_product":round(new_d63,3),"n_product":round(new_n,3),
            "reduction_ratio":rr,"crusher_type":crusher_type}
 
WORK_INDICES = {
    "Limestone":11.6,"Granite":15.1,"Quartz":13.6,"Iron Ore":14.8,
    "Copper Ore":13.1,"Coal":11.4,"Cement Clinker":13.5,
    "E-waste (PCB)":18.0,"Recycled Concrete":12.5,"Recycled Glass":10.8,
}
 
if __name__ == "__main__":
    sizes, passing = generate_sieve_data(d50=5.0, spread=0.8)
    rr = fit_rosin_rammler(sizes, passing)
    ggs = fit_ggs(sizes, passing)
    print("═"*50)
    print("  PARTICLE ANALYSIS RESULTS")
    print("═"*50)
    print(f"  Rosin-Rammler: d63={rr['d63']}mm, n={rr['n']}")
    print(f"  GGS: d_max={ggs['d_max']}mm, m={ggs['m']}")
    E = bond_energy(13.6, 5000, 500)
    print(f"  Bond energy (Quartz 5mm→0.5mm): {E:.2f} kWh/ton")
