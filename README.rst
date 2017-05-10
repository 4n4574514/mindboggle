==============================================================================
Software
==============================================================================
.. role:: red

Mindboggle's open source brain morphometry platform takes in preprocessed T1-weighted
MRI data, and outputs volume, surface, and tabular data containing label, feature, and shape
information for further analysis. Mindboggle can be run on the command line as "mindboggle"
and also exists as a cross-platform Docker container for convenience and reproducibility
of results. The software runs on Linux and is written in Python 3 and Python-wrapped C++ code 
called within a `Nipype <http://nipy.org/nipype>`_ pipeline framework. 
We have tested the software most extensively with Python 3.5.1 on Ubuntu Linux 14.04.

..
    1. Referencing Mindboggle
    2. Support, bugs, and help
    3. Installing Mindboggle
    4. Running Mindboggle
    5. Preprocessing
    6. Processing steps
    7. Output

:Release: |version|
:Date: |today|

Links:

.. toctree::
    :maxdepth: 1

    FAQ <faq.rst>
    license

- `GitHub <http://github.com/nipy/mindboggle>`_ and `Circleci tests <https://circleci.com/gh/nipy/mindboggle>`_
- `Contributors <http://mindboggle.info/people.html>`_

* :ref:`modindex`
* :ref:`genindex`

------------------------------------------------------------------------------
Referencing Mindboggle
------------------------------------------------------------------------------
A Klein, SS Ghosh, FS Bao, J Giard, Y Hame, E Stavsky, N Lee, B Rossa, M Reuter, EC Neto, A Keshavan. 2017. 
**Mindboggling morphometry of human brains**. 
*PLoS Computational Biology* 13(3): e1005350. `doi:10.1371/journal.pcbi.1005350 <http://dx.doi.org/10.1371/journal.pcbi.1005350>`_

------------------------------------------------------------------------------
Support, bugs, and help
------------------------------------------------------------------------------
If you have any questions about Mindboggle, please post to `NeuroStars <https://neurostars.org/tags/mindboggle/>`_ 
with the tag "mindboggle"; if you have found a bug, big or small,
please `submit an issue <https://github.com/nipy/mindboggle/issues>`_ on GitHub.

To learn about command-line options after installing Mindboggle,
type the following in a terminal window::

    mindboggle -h

------------------------------------------------------------------------------
Installing Mindboggle
------------------------------------------------------------------------------
We recommend installing Mindboggle and its dependencies as a cross-platform
Docker container for greater convenience and reproducibility of results.
All the examples below assume you are using this Docker container,
with the path /home/jovyan/work/ pointing to your host machine.
(Alternatively, Mindboggle can be installed from scratch on a Linux machine
using
`this script <https://raw.githubusercontent.com/nipy/mindboggle/master/install_mindboggle.sh>`_).

1. Install and run Docker on your (macOS, Linux, or Windows) host machine:

    https://docs.docker.com/engine/installation/

2. Download the Mindboggle Docker container (paste command in a terminal window)::

    docker pull bids/mindboggle;

3. Set the path on your host machine for the Docker container to access files ("/Users/arno" in this example), and enter the container's bash shell::

    PATH_ON_HOST=/Users/arno;  # set path on host to access folders
    HOST=/home/jovyan/work;  # path to host from within Docker container

    docker run --rm -ti -v $PATH_ON_HOST:$HOST --entrypoint /bin/bash bids/mindboggle;

------------------------------------------------------------------------------
Before running Mindboggle
------------------------------------------------------------------------------
Mindboggle takes as its input preprocessed brain MR image data.
To get up and running with the `Running Mindboggle`_ examples below,
download and unzip the
`mindboggle_input_example.zip <https://osf.io/3xfb8/?action=download&version=1>`_
directory (455 MB), which contains some example preprocessed data,
and skip this section until you wish to process your own data.
Or download and unzip the
`example_mri_data.zip <https://osf.io/k3m94/?action=download&version=1>`_
directory (29 MB), which contains some example MRI data,
and run the FreeSurfer and ANTs commands below to prepare data for Mindboggle.
More example input and output data can be found
on Mindboggle's `examples <https://osf.io/8cf5z>`_ site.

Mindboggle currently takes output from
`FreeSurfer <http://surfer.nmr.mgh.harvard.edu>`_ (v6 or higher recommended)
and optionally from `ANTs <http://stnava.github.io/ANTs/>`_
(v2.1.0rc3 or higher recommended; this version is included in the Docker app).
To run FreeSurfer and ANTs in the Mindboggle Docker container,
enter the Docker container (Step 3 of
`Installing Mindboggle <http://mindboggle.readthedocs.io/en/latest/#installing-mindboggle>`_)
before proceeding.

**FreeSurfer** generates labeled cortical surfaces, and labeled cortical and
noncortical volumes. Run ``recon-all`` on a T1-weighted IMAGE file
(and optionally a T2-weighted image), and set the output SUBJECT name
as well as the output SUBJECTS_DIR directory::

    HOST=/home/jovyan/work;
    IMAGE=$HOST/example_mri_data/T1.nii.gz;  # set path to image file
    SUBJECT=subject1;  # set output subject name
    SUBJECTS_DIR=$HOST/freesurfer_subjects;  # set path to output folder

    recon-all -all -i $IMAGE -s $SUBJECT -sd $SUBJECTS_DIR;

*Version 6 is recommended because by default it uses Mindboggle’s DKT-100
surface-based atlas (with the DKT31 labeling protocol) to generate labels
on the cortical surfaces and corresponding labels in the cortical and
non-cortical volumes (v5.3 generates these surface labels by default;
older versions require "-gcs DKTatlas40.gcs" to generate these surface labels).*

**ANTs** provides brain volume extraction, segmentation, and
registration-based labeling. To generate the ANTs transforms and segmentation
files used by Mindboggle, run the ``antsCorticalThickness.sh`` script on the
same IMAGE file, set an output PREFIX, and a TEMPLATE path to the
`OASIS-30_Atropos_template <https://osf.io/rh9km/>`_
folder installed in the Docker container
("\\" splits the command for readability)::

    HOST=/home/jovyan/work;
    IMAGE=$HOST/example_mri_data/T1.nii.gz;  # same path to input image file
    ANTS_DIR=$HOST/ants_subjects;  # set path to ANTs output folder
    PREFIX=$ANTS_DIR/subject1/ants;  # set prefix to ANTs output
    TEMPLATE=/opt/data/OASIS-30_Atropos_template;  # installed template folder

    antsCorticalThickness.sh -d 3 -a $IMAGE -o $PREFIX \
      -e $TEMPLATE/T_template0.nii.gz \
      -t $TEMPLATE/T_template0_BrainCerebellum.nii.gz \
      -m $TEMPLATE/T_template0_BrainCerebellumProbabilityMask.nii.gz \
      -f $TEMPLATE/T_template0_BrainCerebellumExtractionMask.nii.gz \
      -p $TEMPLATE/Priors2/priors%d.nii.gz;

------------------------------------------------------------------------------
Running Mindboggle
------------------------------------------------------------------------------
See `Before running Mindboggle`_ above for instructions on how to prepare data
for processing by Mindboggle, or to obtain example data to get started.
To use the Mindboggle Docker container, make sure to enter the Docker
container (Step 3 of
`Installing Mindboggle <http://mindboggle.readthedocs.io/en/latest/#installing-mindboggle>`_) 
before proceeding.

**Set paths:**

For brevity in the Examples below, we set paths in a terminal window::

    HOST=/home/jovyan/work;
    MINDBOGGLED=$HOST/mindboggled;  # set the Mindboggle output folder

To use preprocessed FreeSurfer and ANTs data in mindboggle_input_example/::

    FREESURFER_SUBJECT=$HOST/mindboggle_input_example/freesurfer/subjects/arno;
    ANTS_SUBJECT=$HOST/mindboggle_input_example/ants/subjects/arno;

Or if you have preprocessed data in the Docker container (see `Before running Mindboggle <http://mindboggle.readthedocs.io/en/latest/#before-running-mindboggle>`_)::

    FREESURFER_SUBJECT=$SUBJECTS_DIR/$SUBJECT;
    ANTS_SUBJECT=$ANTS_DIR/$SUBJECT;

**Examples:**

To learn about Mindboggle's command options, type this in a terminal window::

    mindboggle -h

**Example 1:**
This command runs Mindboggle on data run through FreeSurfer but not ANTs::

    mindboggle $FREESURFER_SUBJECT --out $MINDBOGGLED

**Example 2:**
Take advantage of ANTs output as well ("\\" splits for readability)::

    mindboggle $FREESURFER_SUBJECT --out $MINDBOGGLED \
        --ants $ANTS_SUBJECT/antsBrainSegmentation.nii.gz

**Example 3:**
Generate only volume (no surface) labels and shapes::

    mindboggle $FREESURFER_SUBJECT --out $MINDBOGGLED \
        --ants $ANTS_SUBJECT/antsBrainSegmentation.nii.gz \
        --no_surfaces

------------------------------------------------------------------------------
Mindboggle processing steps
------------------------------------------------------------------------------
The following steps are performed by Mindboggle (with links to code on GitHub):

1. Create hybrid gray/white segmentation from FreeSurfer and ANTs output (`combine_2labels_in_2volumes <https://github.com/nipy/mindboggle/blob/master/mindboggle/guts/segment.py#L1660>`_).
2. Fill hybrid segmentation with FreeSurfer- or ANTs-registered labels.
3. Compute volume shape measures for each labeled region:

    - volume (`volume_per_brain_region <https://github.com/nipy/mindboggle/blob/master/mindboggle/shapes/volume_shapes.py#L14>`_)
    - thickness of cortical labels (`thickinthehead <https://github.com/nipy/mindboggle/blob/master/mindboggle/shapes/volume_shapes.py#L132>`_)

4. Compute surface shape measures for every cortical mesh vertex:

    - `surface area <https://github.com/nipy/mindboggle/blob/master/vtk_cpp_tools/PointAreaComputer.cpp>`_
    - `travel depth <https://github.com/nipy/mindboggle/blob/master/vtk_cpp_tools/TravelDepth.cpp>`_
    - `geodesic depth <https://github.com/nipy/mindboggle/blob/master/vtk_cpp_tools/geodesic_depth/GeodesicDepthMain.cpp>`_
    - `mean curvature <https://github.com/nipy/mindboggle/blob/master/vtk_cpp_tools/curvature/CurvatureMain.cpp>`_
    - convexity (from FreeSurfer)
    - thickness (from FreeSurfer)

5. Extract cortical surface features:

    - `folds <https://github.com/nipy/mindboggle/blob/master/mindboggle/features/folds.py>`_
    - `sulci <https://github.com/nipy/mindboggle/blob/master/mindboggle/features/sulci.py>`_
    - `fundi <https://github.com/nipy/mindboggle/blob/master/mindboggle/features/fundi.py>`_

6. For each cortical surface label/sulcus, compute:

    - `area <https://github.com/nipy/mindboggle/blob/master/vtk_cpp_tools/area/PointAreaMain.cpp>`_
    - mean coordinates: `means_per_label <https://github.com/nipy/mindboggle/blob/master/mindboggle/guts/compute.py#L512>`_
    - mean coordinates in MNI152 space
    - `Laplace-Beltrami spectrum <https://github.com/nipy/mindboggle/blob/master/mindboggle/shapes/laplace_beltrami.py>`_
    - `Zernike moments <https://github.com/nipy/mindboggle/blob/master/mindboggle/shapes/zernike/zernike.py>`_

7. Compute statistics (``stats_per_label`` in `compute.py <https://github.com/nipy/mindboggle/blob/master/mindboggle/guts/compute.py#L716>`_) for each shape measure in #4 for each label/feature:

    - median
    - median absolute deviation
    - mean
    - standard deviation
    - skewhttps://github.com/nipy/mindboggle/blob/master/mindboggle/shapes/volume_shapes.py#L132
    - kurtosis
    - lower quartile
    - upper quartile

------------------------------------------------------------------------------
Mindboggle output
------------------------------------------------------------------------------
Example output data can be found
on Mindboggle's `examples <https://osf.io/8cf5z>`_ site on osf.io.
By default, output files are saved in $HOME/mindboggled/SUBJECT, where $HOME
is the home directory and SUBJECT is a name representing the person's
brain that has been scanned.
Volume files are in `NIfTI <http://nifti.nimh.nih.gov>`_ format,
surface meshes in `VTK <http://www.vtk.org/>`_ format,
and tables are comma-delimited.
Each file contains integers that correspond to anatomical :doc:`labels <labels>`
or features (0-24 for sulci).
All output data are in the original subject's space.
The following include outputs from most, but not all, optional arguments.

+----------------+----------------------------------------------------+--------------+
|   **Folder**   | **Contents**                                       | **Format**   |
+----------------+----------------------------------------------------+--------------+
|    labels/     |  number-labeled surfaces and volumes               | .vtk, .nii.gz|
+----------------+----------------------------------------------------+--------------+
|    features/   |  surfaces with features:  sulci, fundi             | .vtk         |
+----------------+----------------------------------------------------+--------------+
|    shapes/     |  surfaces with shape measures (per vertex)         | .vtk         |
+----------------+----------------------------------------------------+--------------+
|    tables/     |tables of shape measures (per label/feature/vertex) | .csv         |
+----------------+----------------------------------------------------+--------------+

**mindboggled** / $SUBJECT /

    **labels** /

        **freesurfer_wmparc_labels_in_hybrid_graywhite.nii.gz**:  *hybrid segmentation filled with FS labels*

        **ants_labels_in_hybrid_graywhite.nii.gz**:  *hybrid segmentation filled with ANTs + FS cerebellar labels*

        [left,right]_cortical_surface / **freesurfer_cortex_labels.vtk**: `DKT <http://mindboggle.info/data.html>`_ *cortical surface labels*

    **features** / [left,right]_cortical_surface /

            **folds.vtk**:  *(unidentified) depth-based folds*

            **sulci.vtk**:  *sulci defined by* `DKT <http://mindboggle.info/data.html>`_ *label pairs in depth-based folds*

            **fundus_per_sulcus.vtk**:  *fundus curve per sulcus*  **-- UNDER EVALUATION --**

            **cortex_in_MNI152_space.vtk**:  *cortical surfaces aligned to an MNI152 template*

    **shapes** / [left,right]_cortical_surface /

            **area.vtk**:  *per-vertex surface area*

            **mean_curvature.vtk**:  *per-vertex mean curvature*

            **geodesic_depth.vtk**:  *per-vertex geodesic depth*

            **travel_depth.vtk**:  *per-vertex travel depth*

            **freesurfer_curvature.vtk**:  *FS curvature files converted to VTK*

            **freesurfer_sulc.vtk**:  *FS sulc (convexity) files converted to VTK*

            **freesurfer_thickness.vtk**:  *FS thickness files converted to VTK*

    **tables** /

        **volume_per_freesurfer_label.csv**:  *volume per FS label*

        **volumes_per_ants_label.csv**:  *volume per ANTs label*

        **thickinthehead_per_freesurfer_cortex_label.csv**:  *FS cortex label thickness*

        **thickinthehead_per_ants_cortex_label.csv**:  *ANTs cortex label thickness*

        [left,right]_cortical_surface /

            **label_shapes.csv**:  *per-label surface shape statistics*

            **sulcus_shapes.csv**:  *per-sulcus surface shape statistics*

            **fundus_shapes.csv**:  *per-fundus surface shape statistics*  **-- UNDER EVALUATION --**

            **vertices.csv**:  *per-vertex surface shape statistics*

