from scipy.optimize import newton
from atmosphere import isa
from utilities import calc_D, calc_M
from hx_design import hx
from atmosphere import isa
from numpy import linspace, array, interp
from matplotlib.pyplot import plot, show, xlabel, ylabel, legend, title
from math import pi

# def calc_coefficients(x0, *args):
#     # Extract inputs
#     p01 = x0[0]
#     T01 = x0[1]
#     p02 = x0[2]
#     T02 = x0[3]
#     pe = x0[4]
#     Te = x0[5]
#     Me = x0[6]
#
#     # Extract variables passed through args
#     alt = args[0]
#     M = args[1]
#     prf = args[2]
#     # An = args[3]
#
#     # Air
#     gamma = 1.4
#     R = 287.05  #  J / kg - K
#
#     # free stream conditions
#     pa, pta, Ta, Tta, rhoa = isa(alt, M)
#     T0a = Ta * (1 + (gamma - 1) / 2 * M**2)
#     p0a = pa * (1 + (gamma - 1) / 2 * M**2)**(gamma / (gamma - 1))
#     u = M * (gamma * R * Ta)**0.5
#
#     # isentropic diffuser
#     r1 = p01 - p0a
#     r2 = T01 - T0a
#
#     # fan pressure ratio
#     r3 = p02 - p01 * prf
#     r4 = T02 - T01 * (1 + (prf**((gamma - 1) / gamma) - 1))
#
#     # isentropic nozzle
#     T0e = T02
#     p0e = p02
#
#     r5 = pe - pa
#     r7 = Me - ((2 / (gamma - 1)) * ((p0e / pe)**((gamma - 1) / gamma) - 1))**0.5
#
#     if Me > 1:  # check if nozzle is choked
#         # print('Fan nozzle is choked.')
#         r7 = Me - 1
#         r5 = pe - p0e * (1 + ((gamma - 1) / 2) * Me**2)**(-1 * gamma / (gamma - 1))
#
#     r6 = Te - T0e / (1 + ((gamma - 1) / 2) * Me**2)
#
#     res = [r1, r2, r3, r4, r5, r6, r7]
#     return res

def calc_coefficients(alt, mach, prf):
    # Air
    gamma = 1.4
    R = 287.05  # J / kg - K

    # free stream conditions
    [pa, p0a, Ta, T0a, rho] = isa(alt, mach)
    u = mach * (gamma * R * Ta)**0.5

    # isentropic diffuser
    T01 = T0a
    p01 = p0a

    # fan pressure ratio
    p02 = p01 * prf
    T02 = T01 * (1 + (prf**((gamma - 1) / gamma) - 1))

    # isentropic nozzle
    T0e = T02
    p0e = p02
    pe = pa
    Me = ((2 / (gamma - 1)) * ((p0e / pe)**((gamma - 1) / gamma) - 1))**0.5
    if Me > 1:  # check if nozzle is choked
        print('Fan nozzle is choked.')
        Me = 1
        pe = p0e * (1 + ((gamma - 1) / 2) * Me**2)**(-1 * gamma / (gamma - 1))
    else:
        print('Fan nozzle is not choked. M_e = {}'.format(Me))

    Te = T0e / (1 + ((gamma - 1) / 2) * Me**2)
    ue = Me * (gamma * R * Te)**0.5
    De = Me / ((1 + ((gamma - 1) / 2) * Me**2)**(0.5 * (gamma + 1) / (gamma - 1)))

    cp = ((De * p0e * gamma**0.5) / (R * T0e)**0.5) * (gamma * R / (gamma - 1)) * T01 * (prf - 1)**(
                (gamma - 1) / gamma) / (0.5 * rho * u**3)
    cfx = (((De * p0e * gamma**0.5) / (R * T0e)**0.5) * (ue - u) + (pe - pa)) / (0.5 * rho * u**2)

    # Calculate Mach and Areas at each station
    # Station 2
    D2 = De
    M2 = calc_M(D2, gamma)

    # Station 1
    M1 = M2
    D1 = calc_D(M1, gamma)

    # Station Inlet
    Di = D1 * Ad
    Mi = calc_M(Di, gamma)

    station_mach = [Mi, M1, M2, Me]

    return cp, cfx, station_mach

def calc_thrust(alt, mach, prf, mdot):
    # Air
    gamma = 1.4
    R = 287.05  # J / kg - K

    # free stream conditions
    [pa, p0a, Ta, T0a, rho] = isa(alt, mach)
    u = mach * (gamma * R * Ta)**0.5

    # isentropic diffuser
    T01 = T0a
    p01 = p0a

    # fan pressure ratio
    p02 = p01 * prf
    T02 = T01 * (1 + (prf**((gamma - 1) / gamma) - 1))

    # isentropic nozzle
    T0e = T02
    p0e = p02
    pe = pa
    Me = ((2 / (gamma - 1)) * ((p0e / pe)**((gamma - 1) / gamma) - 1))**0.5
    if Me > 1:  # check if nozzle is choked
        print('Fan nozzle is choked.')
        Me = 1
        pe = p0e * (1 + ((gamma - 1) / 2) * Me**2)**(-1 * gamma / (gamma - 1))
    else:
        print('Fan nozzle is not choked. M_e = {}'.format(Me))

    Te = T0e / (1 + ((gamma - 1) / 2) * Me**2)
    ue = Me * (gamma * R * Te)**0.5
    De = Me / ((1 + ((gamma - 1) / 2) * Me**2)**(0.5 * (gamma + 1) / (gamma - 1)))

    # Calculate Area
    Ae = mdot * (R * T0e)**0.5 / De / p0e / (gamma)**0.5

    power = mdot * cp * (T02 - T01)
    thrust = mdot * (ue - u) + Ae * (pe - pa)

    return power, thrust

if __name__ == "__main__":

    # # Generate initial guess
    # alt = 10972  # m
    # mach = 0.78
    # gamma = 1.4
    # R = 287
    # Cp = gamma * R / (gamma - 1)
    # pa, pta, Ta, Tta, rhoa = isa(alt, mach)
    # ua = mach * (gamma * R * Ta) ** 0.5
    # prf = 1.5
    #
    # p0a = pa + 0.5 * rhoa * ua**2
    # T0a = Ta + ua**2 / 2 / Cp
    #
    # # Generate initial guess
    # x0 = [p0a, T0a, p0a, T0a, pa, Ta, 1.0]
    #
    # root = newton(calc_coefficients, x0, args=(alt, mach, prf), tol=1E-8, maxiter=50)
    # print(root)
    #
    # # Calculate Mach and Areas at each station
    # p01 = root[0]
    # T01 = root[1]
    # p02 = root[2]
    # T02 = root[3]
    # pe = root[4]
    # Te = root[5]
    # Me = root[6]
    #
    # # Station 2
    # D2 = De * An
    # M2 = calc_M(D2, gamma)
    #
    # # Station 1
    # M1 = M2
    # D1 = calc_D(M1, gamma)
    #
    # # Station Inlet
    # Di = D1 * Ad
    # Mi = calc_M(Di, gamma)
    #
    # station_mach = [Mi, M1, M2, Me]
    #
    # ue = Me * (gamma * R * Te)**0.5
    # De = Me / ((1 + ((gamma - 1) / 2) * Me**2)**(0.5 * (gamma + 1) / (gamma - 1)))
    #
    # cp = ((De * p0e * gamma**0.5) / (R * T0e)**0.5) * (gamma * R / (gamma - 1)) * T01 * (prf - 1)**((gamma - 1) / gamma) / (0.5 * rho * u**3)
    # cfx = (((De * p0e * gamma**0.5) / (R * T0e)**0.5) * (ue - u) + (pe - pa)) / (0.5 * rho * u**2)

    # Generate initial guess
    alt = 10972  # m
    mach = 0.78

    # Area ratios
    # An = Ae / A2
    An = 1.0
    # Ad = 1 / Ai
    Ad = 1.0

    prf_var = linspace(1.2, 1.8, 6)
    cp_plot = []
    cfx_plot = []
    power_plot = []
    thrust_plot = []

    # 737 engine
    D_fan = calc_D(0.6, 1.4)
    R = 287
    p, p_t, T, T_t, rho = isa(alt, mach)
    d_fan = 1.76  # [m]
    a_fan = 0.25 * pi * d_fan ** 2
    m_dot = 3 * a_fan * p_t * 1.4 ** 0.5 * D_fan / (R * T_t) ** 0.5
    print('m_dot: {} kg/s'.format(m_dot))

    for prf in prf_var:
        # Calculate coefficients
        cp, cfx, station_mach = calc_coefficients(alt, mach, prf)
        cp_plot.append(cp)
        cfx_plot.append(cfx)
        # Calculate thrust and power
        power, thrust = calc_thrust(alt, mach, prf, m_dot)
        power_plot.append(2 * power / 1000)
        thrust_plot.append(thrust / 1000)

    # Plot
    plot(cfx_plot, cp_plot, label='Turbofan')
    xlabel(r'Thrust Coefficient, $C_{F_{x}}$')
    ylabel(r'Power Coefficient, $C_{P}$')
    legend()
    show()

    # Plot
    plot(thrust_plot, power_plot, label='Turbofan')
    legend()
    xlabel(r'Thrust, [kN]')
    ylabel(r'Power [kW]')
    show()

    # Plot
    drag_737 = 54.1  # [kN]
    p_737 = interp(drag_737, thrust_plot, power_plot)
    plot(power_plot, thrust_plot, label='Turbofan')
    plot(p_737, drag_737, marker='o', color='tab:red', ls='None', label='B737-800 Cruise')
    # plot(power_plot, thrust_plot_hx, label='Heat Exchanger')
    xlabel(r'Power [kW]')
    ylabel(r'Thrust, [kN]')
    title('One-Engine')
    legend()
    show()




