import numpy as np
import requests
import json

def get_api_path():
    return 'http://api.brain-map.org/api/v2/data'

def download_specimen(specimen_name):
    
    service = get_api_path()
    result = requests.get('%s/Specimen/query.json?criteria=[name$eq\'%s\']&include=alignment3d' % (service,specimen_name)).json()
    specimen = result.pop('msg')[0]
    x = specimen['alignment3d']
    alignment_data = np.array([x['trv_%02d' % ii] for ii in range(12)])
    M1 = alignment_data[:9].reshape((3,3))
    M2 = alignment_data[9:].reshape((3,1))
    M3 = np.array([[0,0,0,1]])
    specimen['alignment3d'] = np.vstack((np.hstack((M1, M2)), M3))

    return specimen, result

def get_mni_transform_matrix(specimen_name):
    
    specimen, result = download_specimen(specimen_name)
    assert result['success'] == True

    mni_transform_matrix = specimen['alignment3d']
    assert mni_transform_matrix.shape == (4,4)

    return mni_transform_matrix


if __name__ == "__main__":

    specimen_name = 'H0351.2001'
    mni_transform_matrix = get_mni_transform_matrix(specimen_name)
    