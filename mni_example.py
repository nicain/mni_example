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

def to_mni(input_vals, M):
    
    assert input_vals.shape[0] == 3 

    if input_vals.ndim == 1:
        input_vals_pad = np.hstack((input_vals, np.array([1])))
        return M.dot(input_vals_pad)[:3]
        
    elif input_vals.ndim == 2:
        input_vals_pad = np.vstack((input_vals, np.ones((1,input_vals.shape[1]))))
        return M.dot(input_vals_pad)[:3,:]

    else:
        raise RuntimeError('invalid input shape')

if __name__ == "__main__":

    # specimen_name = 'H0351.2001'
    # mni_transform_matrix = get_mni_transform_matrix(specimen_name)
    # x = np.array([[74, 96, 29],[ 129, 78, 81], [94,102,26], [145,75,66]]).T
    # print to_mni(x, mni_transform_matrix)

    specimen_name = 'H0351.2002'
    mni_transform_matrix = get_mni_transform_matrix(specimen_name)
    x = np.array([[104, 101, 54]]).T
    print to_mni(x, mni_transform_matrix)

    print requests.get('http://api.brain-map.org/api/v2/data/query.json?criteria=model::Donor,\
            rma::criteria,products[abbreviation$eq\'HumanMA\'], \
            rma::include,specimens[parent_id$eqnull](alignment3d), \
            rma::options[only$eq\'donors.id,donors.name,specimens.id\']').json()
