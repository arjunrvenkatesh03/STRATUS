# ga_repo

# Overview
Repository that contains the files to read CALIPSO Virtical Feature Mask (VFM), and Lidar backscattering files from the CALIPSO NASA subsetting website, and parse them for the datasets and metadata stored within - in the future requesting CALIPSO files should not have to be done manually, instead use the XML request file format to automate the file request proccess. 

1) Read and Parse HDF CALIPSO Files - takes in filename and returns dataset, as well as mapped latitude, longitude, altitude arrays (and any other metadata of interest)
2) Homogenize pixel/voxel size for ease of simulation - In VFM simulation this homogenisation is done through array splicing onto arrays that represent 3D space is a uniform manner. For the backscattering data this is done by linear interpolation to ensure homogenous spatial parameters.
3) Create sample points for simulation - currently set up so that points are sample from a normal distribution around the specified altitudes of interest (source/destination), and uniformly in all other spatial dimensions
4) Path Simulation - uses Bresenham's Line algorithm to connect two pixels/voxels and stores the points that the path connects
5) Statistical Analysis - for VFM simulation, this is simply documenting whether pixels encountered on the line path that the Path Simulation calculates are cloud or not. Returns the percentage of all simulated paths through 3D space encoutered clouds. Backscattering Statistical Analysis is still a work in progress.

# How to Run

1) Pull this Repository into your Desktop
2) Make a folder called CALIPSO_L1_Data - or CALIPSO_VFM_Data - and put it in the folder of the simulation you want to run
3) Open the file called "calipso_backscatter_main.py" -- if you want to run VFM simulation instead open "calipso_project_main.py" -- in VS Code or you editor of choice
4) Run and wait for output : should be a png graph of the dataset in the file specified in the simulation main file as well as statistical summary of the simulation. You can check to see if it looks right by plotting in ccplot or VOCAL, or on the CALIPSO main website (First Link), NASA publishes images of all the datasets that are publically available

# Useful/Related Resources
1) https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/   |   CALIPSO User Guide Homepage
2) http://hdfeos.org/zoo/index_openLaRC_Examples.php#CALIPSO    | HDF_EOS example parsing and visualisation of CALIPSO files
3) http://fhs.github.io/pyhdf/index.html  |   documentation for pyhdf python module for reading and parsing HDF files
4) https://ccplot.org/   |  CCPLOT, tool for visualizing CALIPSO data ---- similair tool called VOCAL, which uses ccplot and has some additional GUI attached (problem is that it runs using Python 2.7, and probably has some wack package and code dependencies that might be more trouble than it's worth --- caveat I haven't actually tried using VOCAL)

# Contact

Feel free to use whatever code you want, I try to generally comment out my code as well as I can, but (disclaimer), I'm not a CS guy so if you want any help on deciphering my code, or any associated questions about how to use the code you can contact me at (619)306-8830. Or if you prefer email my email is pvollrath392@gmail. 

# Random Stuff
* code makes use of numba python library to speed up the calculations. Numba precombiles certain functions in the code (functions that use numba are led by @njit). Numba significalty speeds up calculations at large scale but only works with certain packages and libraries (i.e numpy, scipy). When making additions to the code, makes sure that additions that are not compatible with numba are not fed to numba to be precompiled because that will significantly increase runtime. For additional resources about how and why precompiling these functions speeds up the script there are a lot of resurces that go into great technical depth about Python as an interpreted language (vs. compiled) which give it a lot of nice flexible features, but at the cost of making the script significantly slower than other comparable programming languages such as C++. 
