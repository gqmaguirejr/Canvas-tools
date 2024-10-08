# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# Some acronyms from courses and theses in SCI
#
# on 2024-04-26 the merged words and corrected abstracts were separated out into their own files
#
# on 2024-06-23 put the acronyms into this file
#
# 2024-10-04
#
# G. Q. Maguire Jr.
#
# well_known_acronyms_list is a list of acronym_:entries
#   The list structure has been used becuase there can be many different
#   means for a given acronym.
#
# Each acronym_:entry is a list and has the form:
#  acronym, expanded_form, extras_dict
#
#  Note that the optional extras_dict can contain the following keys and values:
#   's': list of sources
#           each source is s string, typeically of the form: 'diva2:ddddddd'
#   'cefr': string containing a CEFR level, such as 'B2'
#

# consider adding support for these
well_known_acronyms_list=[
    # the following are from SCI
    ['ADAS', 'Advanced Driver Assistance Systems', {'s': 'diva2:1380104'}],
    ['AD', 'Autonomous Driving', {'s': 'diva2:1380104'}],
    ['ARWS', 'Active Rear Wheel steering', {'s': 'diva2:1380104'}],
    ['SMC', 'Sliding Mode Control', {'s': 'diva2:1380104'}],
    ['CR', 'constant radius', {'s': 'diva2:892115'}],
    ['FR', 'frequency response', {'s': 'diva2:892115'}],
    ['SWD', 'sine with dwell', {'s': 'diva2:892115'}],
    ['TRIT', 'throttle release in turn', {'s': 'diva2:892115'}],
    ['ISO', 'International Organization for Standards', {'s': 'diva2:892115'}],
    ['NHTSA', 'National Highway Traffc Safety Administration', {'s': 'diva2:892115'}],
    ['JFD)', 'James Fisher Defence', {'s': 'diva2:1127919'}],
    ['AHSS', 'Advance High-Strengt', {'s': 'diva2:1446465'}],
    ['IIW)', 'International institute of Welding', {'s': 'diva2:1446465'}],
    ['DNV', 'Det Norske Veritas', {'s': 'diva2:796782'}],
    ['GL', 'Germanischer Lloyds', {'s': 'diva2:796782'}],
    ['HSC', 'High Speed Craft', {'s': 'diva2:796782'}],
    ['CCR', 'Counterparty Credit Risk', {'s': 'diva2:1795177'}],
    ['CVA', 'Credit Valuation Adjustment', {'s': 'diva2:1795177'}],
    ['PD', 'Probability of Default', {'s': 'diva2:1795177'}],
    ['CDS', 'Credit Default Swap', {'s': 'diva2:1795177'}],
    ['FG)', 'Fermi golden rule', {'s': 'diva2:1741659'}],
    ['QLE', 'Quasi-Linkage Equilibrium', {'s': 'diva2:1564269'}],
    ['DCA', 'Direct Coupling Analysis', {'s': 'diva2:1564269'}],
    ['AS', 'Ankylosing Spondylitis', {'s': 'diva2:860546'}],
    ['PDAC', 'Pancreatic ductal adenocarcinoma', {'s': 'diva2:1571175'}],
    ['CCN1', 'cellular communication cetworkfactor 1', {'s': 'diva2:1571175'}],
    ['GEM', 'gemcitabine', {'s': 'diva2:1571175'}],
    ['QSD', 'quasistationary distribution', {'s': 'diva2:1736958'}],
    ['OU', 'Ornstein-Uhlenbeck', {'s': 'diva2:1736958'}],
    ['SVR', 'Support Vector Regression', {'s': 'diva2:1443981'}],
    ['ConVRP', 'consistent vehicle routing problem', {'s': 'diva2:1341248'}],
    ['Bi', 'Bingham number', {'s': 'diva2:1528247'}],
    ['Ca', 'capillary numbe', {'s': 'diva2:1528247'}],
    ['$\dot{ε}$', 'extension rate', {'s': 'diva2:1528247'}],
    ['ε<sub>STB</sub>', 'strain-to-break', {'s': 'diva2:1528247'}],
    ['PIANC', 'World Association for Waterborne Transport Infrastructure', {'s': 'diva2:1285486'}],
    ['SPL', 'Sound Pressure Level', {'s': 'diva2:1871683'}],
    ['TBLs', 'turbulent boundary layers', {'s': 'diva2:1423684'}],
    ['GPR', 'Gaussian process regressiong', {'s': 'diva2:1423684'}],
    ['RANS', 'Reynolds-Averaged Navier-Stokes', {'s': 'diva2:1423684'}],
    ['DNS', 'Direct Numerical Simulation', {'s': ['diva2:1423684', 'diva2:1222399']}],
    ['LES', 'Large-Eddy Simulation', {'s': 'diva2:1423684'}],
    ['ZPG' 'zero-pressure-gradient', {'s': 'diva2:1423684'}],
    ['APG', 'adverse-pressure-gradient', {'s': 'diva2:1423684'}],
    ['LCA', 'life cycle assessment', {'s': 'diva2:1183366'}],
    ['ICE', 'Internal Combustion Engine', {'s': 'diva2:1183366'}],
    ['B2C', 'business-to-consumers', {'s': 'diva2:1183366'}],
    ['UAV', 'Unmanned Aerial Vehicles', {'s': 'diva2:1143293'}],
    ['TMS', 'transcranial magnetic stimulation', {'s': 'diva2:1189236'}],
    ['CAD', 'computer-aided design', {'s': 'diva2:894068'}],
    ['CAESES/FFW', 'CAESES/FRIENDSHIP-Framework', {'s': 'diva2:894068'}],
    ['CFD)', 'Computational fluid dynamics', {'s': 'diva2:894068'}],
    ['VOF', 'volume of fluid', {'s': 'diva2:894068'}],
    ['AIS', 'automatic identification system', {'s': 'diva2:894068'}],
    ['BEM', 'boundary element method', {'s': 'diva2:894068'}],
    ['POD', 'Proper Orthogonal Decomposition', {'s': 'diva2:1109465'}],
    ['KMD', 'Koopman Mode Decomposition', {'s': 'diva2:1109465'}],
    ['CMS', 'Calogero- Moser-Sutherland', {'s': 'diva2:1780143'}],
    ['BO', 'Benjamin-Ono', {'s': 'diva2:1780143'}],
    ['ncILW', 'non-chiral Intermediate wave', {'s': 'diva2:1780143'}],
    ['GPS', 'Gradient Power Spectrum', {'s': 'diva2:1896438'}],
    ['GWPS', 'global wavelet power spectrum', {'s': 'diva2:1896438'}],
    ['UKF', 'Unscented Kalman Filter', {'s': 'diva2:1380198'}],
    ['COO', 'Controller Output Observer', {'s': 'diva2:1380198'}],
    ['LIBOR', 'London Interbank Offered Rate'],
    ['FSI', 'fluid-structure interaction', {'s': 'diva2:839875'}],
    ['ALE)', 'Arbitrary Lagrangian-Eulerian', {'s': 'diva2:1609976'}],
    ['SST', 'Shear Stress Transport', {'s': 'diva2:1083080'}],
    ['SFRP', 'Short Fibre Reinforced Polymers', {'s': 'diva2:1334020'}],
    ['RoRo', 'Roll-on Roll-off', {'s': 'diva2:1900951'}],
    ['SC', 'Shaped Charges', {'s': ['diva2:1571111', 'diva2:1573058']}],
    ['PET', 'polyethylene terephthalate', {'s': 'diva2:1791328'}],
    ['PP', 'polypropylene', {'s': 'diva2:1791328'}],
    ['WCA', 'water contact angle', {'s': 'diva2:1791328'}],
    ['MSC', 'MacNeal-Schwendler Corporation'],
    ['DLM', 'Doublet Lattice Method', {'s': 'diva2:1900946'}],
    ['TE', 'transmission error', {'s': 'diva2:1247161'}],
    ['ToFERDA', 'Time-of-flight elastic recoil detection analysis', {'s': 'diva2:1142924'}],
    ['PCB', 'Polychlorinated biphenyls', {'s': 'diva2:642316', 'swe': 'polyklorerade bifenyler'}],
    ['GC', 'Gas Chromatography', {'s': 'diva2:642316', 'swe': 'avgaskromatografi'}],
    ['MS', 'Mass Spectrometer', {'s': 'diva2:642316', 'swe': 'masspektrometer'}],
    ['SNV', 'Svenskanaturvårdsverket', {'s': 'diva2:642316', 'eng': 'Swedish environmental agency'}],
    ['SCR', 'Selective! Catalytic! Reduction', {'s': 'diva2:459344', 'n': 'spelled out in thesis'}],
    ['SYL', 'Sailing Yacht Lab', {'s': 'diva2:1110767'}],
    ['VLM', 'Vortex Lattice Method', {'s': 'diva2:1110767'}],
    ['SPH', 'Smooth Particle Hydrodynamics', {'s': 'diva2:405926'}],
    ['NACA', 'National Advisory Committee for Aeronautics', {'s': 'diva2:405926'}],
    ['DAS', 'DriverAssistance Systems', {'s': 'diva2:618217'}],
    ['AEB', 'automatic emergency brake', {'s': 'diva2:618217'}],
    ['ADAS', 'Advanced driver-assistance systems', {'s': 'diva2:618217'}],
    ['SNGR', 'Stochastic Noise Generation and Radiation', {'s': 'diva2:1857264'}],
    ['SNG', 'Stochastic Noise Generation', {'s': 'diva2:1857264'}],
    ['AO', 'adaptive optics', {'s': 'diva2:1891378'}],
    ['LEO', 'Low-Earth Orbit', {'s': 'diva2:1891378'}],
    ['GEO', 'Geostationary Orbit', {'s': 'diva2:1891378'}],
    ['FRRHs', 'Fiber Reinforced Rubber Hoses', {'s': 'diva2:1900873'}],
    ['HGO', 'Holzapfel-Gasser-Ogden', {'s': 'diva2:1900873'}],
    ['KS', 'Kaliske-Schmidt', {'s': 'diva2:1900873'}],
    ['HAZ', 'Heat Affected Zone', {'s': 'diva2:1740927'}],
    ['HMM', 'hidden Markov model', {'s': ['diva2:1107428', 'diva2:1816899']}],
    ['HMMs', 'hidden Markov models', {'s': ['diva2:1107428', 'diva2:1816899']}],
    ['SLE', 'Systemic Lupus Erythematosu', {'s': 'diva2:1332273'}],
    ['LNA', 'low-noise amplifier', {'s': ['diva2:1692150', 'diva2:1804716']}],
    ['LNAs', 'low-noise amplifiers', {'s': ['diva2:1692150', 'diva2:1804716']}],
    ['qubit', 'quantum bit', {'s': 'diva2:1692150'}],
    ['InP', 'indium phosphide', {'s': 'diva2:1692150'}],
    ['HEMT', 'high-electron-mobility transistor', {'s': ['diva2:1692150', 'diva2:1804716']}],
    ['MCP', 'mixed characteristic polynomial', {'s': 'diva2:1106332'}],
    ['MCPs', 'mixed characteristic polynomials', {'s': 'diva2:1106332'}],
    ['MoDN', 'Modular Decision Support Network', {'s': 'diva2:1859964'}],
    ['MNAR', 'missing not at random', {'s': 'diva2:1859964'}],
    ['MILP', 'mixed integer linear programming', {'s': 'diva2:1349671'}],
    ['MTMD', 'Multiple Tuned Mass Damper', {'s': 'diva2:1707859'}],
    ['OEM', 'Original Equipment Manufacturer', {'s': 'diva2:1707859', 'n': 'not spelled out in abstract'}],
    ['NVH', 'Noise, Vibration, and Harshness', {'s': 'diva2:1707859', 'n': 'noy spelled out in abstract or thesis'}],
    ['FFOCT', 'Full-Field Optical Coherence Tomography', {'s': 'diva2:1695153'}],
    ['LED', 'Light-Emitting Diode', {'s': 'diva2:1695153'}],
    ['SLD', 'Superluminescent Diode', {'s': 'diva2:1695153'}],
    ['OCT', 'Optical Coherence Tomography', {'s': 'diva2:488441'}],
    ['MAO-OCT', 'Multiple-Angle Oblique Optical CoherenceTomography', {'s': 'diva2:488441'}],
    ['HPIF', 'high pass intensity filters', {'s': 'diva2:488441'}],
    ['PRT', 'Personal Rapid Transit', {'s': 'diva2:891537'}],
    ['SEM', 'Soft Extra Muscles system', {'s': 'diva2:839835'}],
    ['CFRP', 'Carbon Fibre Reinforced Plastic', {'s': 'diva2:1528107'}],
    ['UD', 'unidirectional', {'s': 'diva2:1528107'}],
    ['XFEM', 'eXtended Finite Element Method', {'s': 'diva2:562498'}],
    ['PM', 'Particulate matter', {'s': 'diva2:1900930'}],
    ['SAF)', 'sustainable aviation fuel', {'s': 'diva2:1900930'}],
    ['nvPM', 'non-volatile particulate matter', {'s': 'diva2:1900930'}],
    ['FDR', 'Flight data recorder', {'s': 'diva2:1900930', 'swe': 'färdregistratorn'}],
    ['EI', 'Emission index', {'s': 'diva2:1900930'}],
    ['BWB', 'Blended Wing Body', {'s': 'diva2:787508'}],
    ['CEASIOM', 'Computerised Environment for Aircraft Synthesis and Integrated Optimisation Methods', {'s': 'diva2:787508'}],
    ['DLR', 'German Aerospace Centre', {'s': 'diva2:787508'}],
    ['CPACS', 'Common Parametric Aircraft Configuration Scheme', {'s': 'diva2:787508'}],
    ['CC', 'CPACSCreator', {'s': 'diva2:787508'}],
    ['ESP', 'Electronic Stability Program', {'s': 'diva2:1082039'}],
    ['TCS', 'Traction Control System', {'s': 'diva2:1082039'}],
    ['FDTD', 'Finite Difference Time Domain', {'s': 'diva2:1527799'}],
    ['FEM', 'finite elements', {'s': 'diva2:1527799'}],
    ['MBS', 'multibody simulation', {'s': 'diva2:1527796'}],
    ['TFG', 'true flat ground', {'s': 'diva2:653271'}],
    ['STBR)', 'single track ballast and rail', {'s': 'diva2:653271'}],
    ['ABL', 'atmospheric boundary layer', {'s': 'diva2:653271'}],
    [ "Cmx,lee", 'roll moment coefficient about lee rail', {'s': 'diva2:653271'}],
    ['AMS', 'Aeroball Measurement System', {'s': 'diva2:1669916'}],
    ['BNV', 'Det Norske Veritas', {'s': 'diva2:1145330'}],
    ['SA', 'Spalart-Allmaras', {'s': 'diva2:1674019'}],
    ['AOAs', 'angles of attack', {'s': 'diva2:1674019'}],
    ['SST', 'Shear Stress Transport', {'s': 'diva2:1674019'}],
    ['PFD', 'Pelvic Floor Dysfunction', {'s': 'diva2:1890023'}],
    ['PFM', 'Pelvic Floor Muscles', {'s': 'diva2:1890023'}],
    ['MRI', 'Magnetic Resonance Imaging', {'s': 'diva2:1890023'}],
    ['SWE', 'Shear Wave Elastography', {'s': 'diva2:1890023'}],
    ['MRE', 'Magnetic Resonance Elastography', {'s': 'diva2:1890023'}],
    ['PVA', 'Polyvinyl Alcohol', {'s': 'diva2:1890023'}],
    ['GARCH', 'Generalized Autoregressive Conditional Heteroskedasticity', {'s': 'diva2:1894668'}],
    ['VaR', 'Value at Risk', {'s': 'diva2:1894668'}],
    ['GJR-GARCH', 'Glosten-Jagannathan-Runkle GARCH', {'s': 'diva2:1894668'}],
    ['ETFs', 'exchange-traded funds', {'s': 'diva2:1894668'}],
    ['PSH', 'Pumped-Storage Hydroelectricity', {'s': 'diva2:1843160'}],
    ['IAR', 'Integer Ambiguity Resolution', {'s': 'diva2:440412'}],
    ['IA', 'Interval Analysis', {'s': 'diva2:440412'}],
    ['IBIAR', 'Interval Based Integer Am-biguity Resolution', {'s': 'diva2:440412'}],
    ['BOUNDS', 'Bounded integer ambiguity resolution using interval analysis', {'s': 'diva2:440412'}],
    ['NLR', 'Dutch National Aerospace Laboratory', {'s': 'diva2:440412'}],
    ['DUT', 'Delft University of Technology', {'s': 'diva2:440412'}],
    ['SMC', 'Advanced Sheet MouldingCompound (', {'s': 'diva2:618592'}],
    ['RTM', 'Resin Transfer Moulding', {'s': 'diva2:618592'}],
    ['ATT', 'axial tensile test', {'s': 'diva2:1739571'}],
    ['SCADA', 'Supervisory Control And Data Acquisition', {'s': 'diva2:700034'}],
    ['SMB', 'Small minus Big', {'s': 'diva2:1894689'}],
    ['HML', 'High minus Low', {'s': 'diva2:1894689'}],
    ['DLIR', 'Deep Learning Image Reconstruction', {'s': 'diva2:1781504'}],
    ['HMD', 'helmet-/head-mounted displays', {'s': 'diva2:893770'}],
    ['CDTIs', 'cockpit displays of traffic information', {'s': 'diva2:893770'}],
    ['QSD', 'quasistationary distribution', {'s': 'diva2:1736958'}],
    ['PIV', 'Particle Image Velocimetry', {'s': 'diva2:1078086'}],
    ['MTL', 'Minimum Turbulence Level', {'s': 'diva2:1078086'}],
    ['AFM', 'Atomic Force Microscopy', {'s': 'diva2:562186'}],
    ['EDS', 'Electronic Defense Systems', {'s': 'diva2:877595'}],
    ['EW', 'Electronic Warfare', {'s': 'diva2:877595'}],
    ['LSC', 'Life Support Costs', {'s': 'diva2:877595'}],
    ['ILS', 'Integrated Logistics Support', {'s': 'diva2:877595'}],
    ['AUVs', 'autonomous underwater vehicles', {'s': 'diva2:1380300'}],
    ['MOKE)', 'Magneto-Optical Kerr Effect', {'s': 'diva2:430778'}],
    ['tr-MOKE', 'time-resolved MOKE', {'s': 'diva2:430778'}],
    ['NPs', 'Nanoparticles', {'s': 'diva2:1737092'}],
    ['SPIONs', 'Superparamagnetic iron oxidenanoparticles', {'s': 'diva2:1737092'}],
    ['MRI', 'magnetic resonance imagining', {'s': 'diva2:1737092'}],
    ['NCs', 'nanoclusters', {'s': 'diva2:1737092'}],
    ['MW', 'microwave-assisted', {'s': 'diva2:1737092'}],
    ['ST', 'conventional solvothermal', {'s': 'diva2:1737092'}],
    ['ML', 'Machine Learning', {'s': 'diva2:1720668'}],
    ['CV', 'Computer Vision', {'s': 'diva2:1720668'}],
    ['OBIR', 'Object Based Image Retrieval', {'s': 'diva2:1720668'}],
    ['YOLO', 'You Only Look Once', {'s': 'diva2:1720668'}],
    ['GroWiKa', 'Großer Windkannal', {'s': 'diva2:1040728'}],
    ['HFI', 'Hermann-Föttinger Institute', {'s': 'diva2:1040728'}],
    ['BeRT', 'Reasearch Wind Turbine', {'s': 'diva2:1040728'}],
    ['CROR', 'means Contra-Rotating Open Rotor', {'s': 'diva2:839847'}],
    ['MPC', 'Model Predictive Control', {'s': 'diva2:1795471'}],
    ['LSTM', 'Long Short Term Memory', {'s': 'diva2:1795471'}],
    ['SA', 'Simulated Annealing', {'s': 'diva2:1795471'}],
    ['GDP', 'gross domestic product', {'s': 'diva2:1334745'}],
    ['CCN1', 'cellular communication network factor 1', {'s': 'diva2:1571175'}],
    ['PDAC', 'Pancreatic ductal adenocarcinoma', {'s': 'diva2:1571175'}],
    ['GEM)', 'gemcitabine', {'s': 'diva2:1571175'}],
    ['FABVs', 'Fast Acting Braking Valves', {'s': 'diva2:1183292'}],
    ['FPs', 'financial participants', {'s': 'diva2:1799827'}],
    ['CRR', 'Capital Requirements Regulation', {'s': 'diva2:1799827'}],
    ['A-SA', 'Alternative Standardised Approach', {'s': 'diva2:1799827'}],
    ['A-IMA', 'Alternative Internal Model Approach', {'s': 'diva2:1799827'}],
    ['ES', 'Expected Shortfall', {'s': 'diva2:1799827'}],
    ['RNN', 'recurrent neural network', {'s': 'diva2:1799827'}],
    ['RTM', 'High pressure RTM (H', {'s': 'diva2:919302'}],
    ['CoxPH', 'Cox Proportional Hazard', {'s': 'diva2:1849673'}],
    ['EKN', 'Exportkreditnämnden', {'s': 'diva2:1849673', 'eng': 'Swedish export credit agency'}],
    ['KAIST', 'Korean Advanced Institute of Science and Technology', {'s': 'diva2:1843148'}],
    ['EOS', 'Equation of State', {'s': 'diva2:1695944'}],
    ['dpa', 'displacements per atom', {'s': 'diva2:1739571'}],
    ['dpa/year', 'displacements per atom', {'s': 'diva2:420212'}],
    ['dwfs', 'dry water flow solver', {'s': 'diva2:545172'}],
    ['PTO', 'Power Take-off', {'s': 'diva2:783984'}],
    ['CPO', 'CorPower Ocean', {'s': 'diva2:783984'}],
    ['WEC', 'Wave Energy Converters', {'s': 'diva2:783984'}],
    ['FSI', 'fluid-structure interaction', {'s': 'diva2:839875'}],
    ['POD', 'proper orthogonal decomposition method', {'s': 'diva2:963050'}],
    ['FP', '”Fingerprintization', {'s': 'diva2:1720668'}],
    ['EVT', 'Extreme Value Theory', {'s': 'diva2:1761921'}],
    ['GANs', 'General Adversarial Networks', {'s': 'diva2:1761921'}],
    ['AESIR', 'Association of EngineeringStudents in Rocketry', {'s': 'diva2:1673875'}],
    ['LiDAR', 'Light Detection And Ranging', {'s': 'diva2:1571710'}],
    ['SNSPD', 'single photondetector', {'s': 'diva2:1571710'}],
    ['OTDR', 'Optical Time Domain reflectrometry', {'s': 'diva2:1571710'}],
    ['GRBs', 'Gamma ray bursts', {'s': 'diva2:740888'}],
    ['MDP', 'minimum detectable polarisation', {'s': 'diva2:740888'}],
    ['VIX', 'volatility index', {'s': 'diva2:1432665'}],
    ['DRL)', 'Deep Reinforcement Learning', {'s': 'diva2:1849139'}],
    ['PPO', 'Proximal policy optimization', {'s': 'diva2:1849139'}],
    ['OMXS30', 'OMX Stockholm 30 index', {'s': 'diva2:1849139'}],
    ['HWA', 'hot-wire anemometry', {'s': 'diva2:1081137	'}],
    ['TMF', 'thermomechancial loads', {'s': 'diva2:1448896'}],
    ['HCF', 'high cycle fatigue load', {'s': 'diva2:1448896'}],
    ['LGI', 'lamellar graphite iron', {'s': 'diva2:1448896'}],
    ['CGI', 'compacted graphite iron', {'s': 'diva2:1448896'}],
    ['TWPA', 'traveling wave parametric amplifier', {'s': 'diva2:1682167'}],
    ['BDM', 'Brezzi-Douglas-Marini-elements', {'s': 'diva2:1849663'}],
    ['NEST', 'Neural Simulation Tool', {'s': 'diva2:753649'}],
    ['STDP', 'Spike-Timing Dependent Plasticity', {'s': 'diva2:753649'}],
    ['UN', 'uranium mononitride', {'s': 'diva2:1764265'}],
    ['SRIM', 'Stopping and Range of Ions in Matter', {'s': 'diva2:1764265'}],
    ['XRD', 'X-Ray diffraction', {'s': 'diva2:1764265'}],
    ['SEM', 'scanning electron microscop', {'s': 'diva2:1764265'}],
    ['EBSD', 'Electron backscatter diffraction', {'s': 'diva2:1764265'}],
    ['FIB', 'Focused ion beam', {'s': 'diva2:1764265'}],
    ['TEM', 'transmission electron microscopy', {'s': 'diva2:1764265'}],
    ['MBSE', 'Model-Based System Engineering', {'s': 'diva2:1613411'}],
    ['SSI', 'soil-structure interaction', {'s': 'diva2:441466'}],
    ['ivf', '<em>in vitro fertilization</em>', {'s': 'diva2:1163154', 'n': 'no full text'}],
    ['AOCS', 'Attitude and Orbital Control Systems', {'s': 'diva2:1078080'}],
    ['PET', 'Positron Emission Tomography', {'s': 'diva2:937846'}],
    ['GATE', 'GEANT4 Application for Tomographic Emission', {'s': 'diva2:937846'}],
    ['MC', 'Monte Carlo', {'s': 'diva2:937846'}],
    ['PBA', 'Prussian Blue Analogue', {'s': 'diva2:1847362'}],
    ['PDS', 'Peroxydisulfate', {'s': 'diva2:1847362'}],
    ['PINN', 'physics-informed neural network', {'s': 'diva2:1709501'}],
    ['LOCA', 'Loss Of Coolant Accident', {'s': 'diva2:839851'}],
    ['sBO', 'spin Benjamin-Ono', {'s': 'diva2:1731898'}],
    ['HWM', 'half-wave maps', {'s': 'diva2:1731898'}],
    ['sCM', 'spin Calogero-Moser', {'s': 'diva2:1731898'}],
    ['rsBO', 'rescaled sBO', {'s': 'diva2:1731898'}],
    ['sncILW', 'spin non-chiral intermediate long-wave', {'s': 'diva2:1731898'}],
    ['ncIHF', 'non-chiral intermediate Heisenberg ferromagnet', {'s': 'diva2:1731898'}],
    ['INTEGRAL', 'INTErnational Gamma-Ray Astrophysics Laboratory', {'s': 'diva2:1082651'}],
    ['SDO', 'Space Debris Office', {'s': 'diva2:1082651'}],
    ['ICBT', 'internet-delivered cognitive behavior therapy', {'s': 'diva2:1218565'}],
    ['CSR', 'clinical severity ratings', {'s': 'diva2:1218565'}],
    ['MTF', 'Modulation Transfer Function', {'s': 'diva2:585833'}],
    ['FOMs', 'Figure of Merits', {'s': 'diva2:585833'}],
    
]
