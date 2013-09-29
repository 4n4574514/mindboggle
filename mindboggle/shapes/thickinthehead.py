#!/usr/bin/python
"""
Compute a simple thickness measure for each labeled gray region.


Authors:
    - Arno Klein, 2013  (arno@mindboggle.info)  http://binarybottle.com

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def thickinthehead(segmented_file, labeled_file, gray_value=2, white_value=3,
                   labels=[], out_dir='', resize=True, propagate=True,
                   use_c3d=False):
    """
    Compute a simple thickness measure for each labeled gray region.

    Note: gray, white, labeled files are all the same coregistered brain.

    Steps:
    1. Extract outer and inner borders of gray voxels.
    2. Compute thickness per label = gray / average border

    Parameters
    ----------
    segmented_file : str
        image volume with gray and white matter labels
    labeled_file : str
        corresponding image volume with index labels
    gray_value : integer
        gray matter label value in segmented_file
    white_value : integer
        white matter label value in segmented_file
    labels : list of integers
        label indices
    out_dir : str
        output directory
    resize : Boolean
        resize (2x) segmented_file for more accurate thickness estimates?
    propagate : Boolean
        propagate labels through gray matter?
    use_c3d : Boolean
        use convert3d? (otherwise ANTs ImageMath)

    Returns
    -------
    thicknesses : list of floats
        thickness values
    labels : list of integers
        label indices

    Examples
    --------
    >>> from mindboggle.shapes.thickinthehead import thickinthehead
    >>> segmented_file = 'brain_seg.nii.gz'
    >>> labeled_file = 'labeled.nii.gz'
    >>> gray_value = 2
    >>> white_value = 3
    >>> labels = []
    >>> out_dir = '.'
    >>> resize = True
    >>> propagate = False
    >>> use_c3d = False
    >>> thicknesses, labels = thickinthehead(segmented_file, labeled_file, gray_value, white_value, labels, out_dir, resize, propagate, use_c3d)

    """
    import os
    import numpy as np
    import nibabel as nb

    #-------------------------------------------------------------------------
    # Output files:
    #-------------------------------------------------------------------------
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    gray = os.path.join(out_dir, 'gray.nii.gz')
    white = os.path.join(out_dir, 'white.nii.gz')
    inner_edge = os.path.join(out_dir, 'gray_inner_edge.nii.gz')
    use_outer_edge = True
    if use_outer_edge:
        outer_edge = os.path.join(out_dir, 'gray_outer_edge.nii.gz')

    #-------------------------------------------------------------------------
    # Extract white and gray matter:
    #-------------------------------------------------------------------------
    if use_c3d:
        cmd = ' '.join(['c3d', segmented_file,
                        '-threshold', str(white_value), str(white_value), '1 0',
                        '-o', white])
        print(cmd)
        os.system(cmd)

        cmd = ' '.join(['c3d', segmented_file,
                        '-threshold', str(gray_value), str(gray_value), '1 0',
                        '-o', gray])
        print(cmd)
        os.system(cmd)
    else:
        cmd = ' '.join(['ThresholdImage 3', segmented_file,
                        white, str(white_value), str(white_value), '1 0'])
        print(cmd)
        os.system(cmd)

        cmd = ' '.join(['ThresholdImage 3', segmented_file,
                        gray, str(gray_value), str(gray_value), '1 0'])
        print(cmd)
        os.system(cmd)

    #-------------------------------------------------------------------------
    # Propagate labels through gray matter (or simply multiply):
    #-------------------------------------------------------------------------
    if propagate:
        args = ['ImageMath', '3', gray, 'PropagateLabelsThroughMask',
                gray, labeled_file]
        cmd = ' '.join(args)
        print(cmd)
        os.system(cmd)
    else:
        if use_c3d:
            cmd = ' '.join(['c3d', gray, labeled_file, '-multiply', '-o', gray])
            print(cmd)
            os.system(cmd)
        else:
            cmd = ' '.join(['ImageMath 3', gray, 'm', gray, labeled_file])
            print(cmd)
            os.system(cmd)

    #-------------------------------------------------------------------------
    # Resample gray and white files:
    #-------------------------------------------------------------------------
    if resize:
        rescale = 2
        rescale_percent = str(rescale * 100)

        if use_c3d:
            cmd = ' '.join(['c3d', gray, '-interpolation nearestneighbor',
                            '-resample '+rescale_percent+'%', '-o', gray])
            print(cmd)
            os.system(cmd)

            cmd = ' '.join(['c3d', white, '-interpolation nearestneighbor',
                            '-resample '+rescale_percent+'%', '-o', white])
            print(cmd)
            os.system(cmd)
        else:

    #-------------------------------------------------------------------------
    # Extract gray inner and outer border voxels:
    #-------------------------------------------------------------------------
    if use_c3d:
        cmd = ' '.join(['c3d', white, '-dilate 1 1x1x1vox',
                        gray, '-multiply', '-o', inner_edge])
        print(cmd)
        os.system(cmd)
        if use_outer_edge:
            cmd = ' '.join(['c3d', gray, '-binarize -erode 1 1x1x1vox',
                            '-threshold 1 1 0 1', gray, '-multiply',
                            '-o', outer_edge])
            print(cmd)
            os.system(cmd)
            cmd = ' '.join(['c3d', inner_edge, '-binarize -threshold 1 1 0 1',
                            outer_edge, '-multiply', '-o', outer_edge])
            print(cmd)
            os.system(cmd)
    else:









        cmd = ' '.join(['ImageMath 3', white, 'D', gray, labeled_file])
        print(cmd)
        os.system(cmd)

    #-------------------------------------------------------------------------
    # Load data:
    #-------------------------------------------------------------------------
    #img = nb.load(gray)
    #hdr = img.get_header()
    #voxel_volume = np.prod(hdr.get_zooms())
    #gray_data = img.get_data().ravel()
    gray_data = nb.load(gray).get_data().ravel()
    inner_edge_data = nb.load(inner_edge).get_data().ravel()
    if use_outer_edge:
        outer_edge_data = nb.load(outer_edge).get_data().ravel()

    #-------------------------------------------------------------------------
    # Loop through labels:
    #-------------------------------------------------------------------------
    thicknesses = []
    if not labels:
        labeled_data = nb.load(labeled_file).get_data().ravel()
        labels = np.unique(labeled_data)
    labels = [int(x) for x in labels]
    for label in labels:

        #---------------------------------------------------------------------
        # Compute thickness as a ratio of label volume and edge volume:
        #---------------------------------------------------------------------
        label_gray_voxels = len(np.where(gray_data==label)[0])
        label_inner_edge_voxels = len(np.where(inner_edge_data==label)[0])
        if label_inner_edge_voxels:
            if use_outer_edge:
                label_outer_edge_voxels = len(np.where(outer_edge_data==label)[0])
                label_edge_voxels = (label_inner_edge_voxels +
                                     label_outer_edge_voxels) / 2.0
            else:
                label_edge_voxels = label_inner_edge_voxels
            thickness = label_gray_voxels / label_edge_voxels
            thicknesses.append(thickness)
            print('label {0} voxels: gray={1:2.2f}, inner_edge={2:2.2f}, '
                  'outer_edge={3:2.2f}, edge={4:2.2f}, thickness={5:2.2f}mm'.
                  format(label, label_gray_voxels, label_inner_edge_voxels,
                  label_outer_edge_voxels, label_edge_voxels, thickness))

    return thicknesses, labels


def run_thickinthehead(subjects, labels, out_dir='', atropos_dir='',
                       atropos_stem='', label_dir='', label_filename=''):
    """
    Combine FreeSurfer volume outputs (no surface-based outputs) to obtain
    a table of simple thickness measures for each labeled region.

    Steps ::

      1. Convert FreeSurfer volumes to nifti format in their original space.
      2. Combine FreeSurfer (and optionally ANTs) gray & white segmentations.
      3. Compute simple thickness per label = gray / average border
      4. Store thickness values in a table.

    Options ::

      1. Include antsCorticalThickness.sh (Atropos) gray matter segmentation.
      2. Use non-FreeSurfer labels.

    Requires ::

        FreeSurfer's mri_vol2vol

    Parameters
    ----------
    subjects : list of strings
        names of FreeSurfer subject directories
    labels : list of integers
        label indices
    out_dir : str (optional)
        output directory
    atropos_dir : str (optional)
        directory containing subject subdirectories with gray matter files
    atropos_stem : str (optional)
        stem prepending name of antsCorticalThickness.sh output files
    label_dir : str (optional)
        directory containing subject subdirectories with label files
    label_filename : str (optional)
        label file name within <label_dir>/<subject>/

    Returns
    -------
    thickness_table : numpy array
        thickness values
    table_file : string
        name of file containing thickness values

    Examples
    --------
    >>> from mindboggle.shapes.thickinthehead import run_thickinthehead
    >>> subjects=['MMRR-21-2','MMRR-21-2_rescan']
    >>> labels = range(1002,1036) + range(2002,2036)
    >>> labels.remove(1004)
    >>> labels.remove(2004)
    >>> labels.remove(1032)
    >>> labels.remove(2032)
    >>> labels.remove(1033)
    >>> labels.remove(2033)
    >>> out_dir = 'thickness_outputs'
    >>> atropos_dir = ''
    >>> atropos_stem = ''
    >>> label_dir = ''
    >>> label_filename = ''
    >>> thickness_table, table_file = run_thickinthehead(subjects, labels, out_dir, atropos_dir, atropos_stem, label_dir, label_filename)

    """
    import os, sys
    import numpy as np
    import nibabel as nb

    from mindboggle.utils.segment import combine_segmentations
    from mindboggle.shapes.thickinthehead import thickinthehead

    subjects_dir = os.environ['SUBJECTS_DIR']

    use_c3d = False
    resize = True
    thickness_table = np.zeros((len(labels), len(subjects)+1))
    thickness_table[:,0] = labels
    for isubject, subject in enumerate(subjects):

        #---------------------------------------------------------------------
        # Outputs:
        #---------------------------------------------------------------------
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        out_subdir = os.path.join(out_dir, subject)
        if not os.path.exists(out_subdir):
            os.mkdir(out_subdir)
        labeled_file = os.path.join(out_subdir, 'labeled.nii.gz')

        #---------------------------------------------------------------------
        # Convert FreeSurfer label volume to nifti format (if no label file):
        #---------------------------------------------------------------------
        if label_filename:
            labeled_file = os.path.join(label_dir, subject, label_filename)
        else:
            aparc = os.path.join(subjects_dir, subject, 'mri', 'aparc+aseg.mgz')
            rawavg = os.path.join(subjects_dir, subject, 'mri', 'rawavg.mgz')

            cmd = ' '.join(['mri_vol2vol --mov', aparc, '--targ', rawavg,
                            '--interp nearest',
                            '--regheader --o', labeled_file])
            print(cmd)
            os.system(cmd)
            cmd = ' '.join(['c3d', labeled_file, '-replace 2 0 41 0',
                            '-o', labeled_file])
            print(cmd)
            os.system(cmd)

        #---------------------------------------------------------------------
        # Include Atropos segmentation:
        #---------------------------------------------------------------------
        if atropos_stem:
            supdir = os.path.join(atropos_dir, subject)
            subdirs = os.listdir(supdir)
            subdir = None
            for subdir1 in subdirs:
                if atropos_stem in subdir1:
                    subdir = subdir1
            if subdir:
                second_segmentation_file = os.path.join(supdir, subdir,
                    atropos_stem + 'BrainSegmentation.nii.gz')
            else:
                sys.exit('No segmentation file for ' + subject)
        else:
            second_segmentation_file = ''

        #---------------------------------------------------------------------
        # Combine FreeSurfer and Atropos segmentations:
        #---------------------------------------------------------------------
        gray_and_white_file = combine_segmentations(subject,
                                                    second_segmentation_file,
                                                    out_subdir, use_c3d)

        #---------------------------------------------------------------------
        # Tabulate thickness values:
        #---------------------------------------------------------------------
        gray_value = 2
        white_value = 3
        propagate = True
        thicknesses, u1 = thickinthehead(gray_and_white_file, labeled_file,
                                         gray_value, white_value, labels,
                                         out_subdir, resize, propagate)

        thickness_table[:, isubject+1] = thicknesses

    #-------------------------------------------------------------------------
    # Save results:
    #-------------------------------------------------------------------------
    table_file = os.path.join(out_dir, 'thicknesses.csv')
    format = ' '.join(['%2.4f' for x in subjects])
    np.savetxt(table_file, thickness_table, fmt='%d ' + format,
               delimiter='\t', newline='\n')

    return thickness_table, table_file


if __name__ == "__main__":

    from mindboggle.shapes.thickinthehead import thickinthehead

    subjects = ['OASIS-TRT-20-1']

    #-------------------------------------------------------------------------
    # Labels:
    #-------------------------------------------------------------------------
    labels = range(1002,1036) + range(2002,2036)
    labels.remove(1004)
    labels.remove(2004)
    labels.remove(1032)
    labels.remove(2032)
    labels.remove(1033)
    labels.remove(2033)

    out_dir = 'thickness_outputs'
    atropos_dir = '/data/export/home/mzia/cluster/data/embarc_hc_anatomicals/'
    atropos_stem = 'tmp'
    label_dir = '' #/public/embarc/embarc_control_labels'
    label_filename = '' #labels.nii.gz'
    thickness_table, table_file = run_thickinthehead(subjects, labels, out_dir,
        atropos_dir, atropos_stem, label_dir, label_filename)
