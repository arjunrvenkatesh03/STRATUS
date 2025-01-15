#module to calculate transmission at specified wavelength from extinction coefficient arrays and visibility arrays

def wavelength_dependence_extCoef(wavelength, extincCoefList532, extincCoefList1064, visibility532, visibility1064):
    #calculate transmission at specified wavelength
    transmission_NWL_upper = []
    transmission_NWL_lower = []
    for i in range(len(extincCoefList532)):
        #calculate extinction coefficient at specified wavelength - visibility bounds are the average of 1064 and 532
        extincCoef_NWL_upper = 3.61/(min(visibility532[i][0],visibility1064[i][0]) * (wavelength/550)**(-0.451))
        extincCoef_NWL_lower = 3.61/(max(visibility532[i][1],visibility1064[i][1]) * (wavelength/550)**(-1.6))

        #calculate transmission at specified wavelength
        transmission_NWL_upper.append(10**(-extincCoef_NWL_upper * 1))
        transmission_NWL_lower.append(10**(-extincCoef_NWL_lower * 1))

    return transmission_NWL_upper, transmission_NWL_lower