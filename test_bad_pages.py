import pickle
import os
year_dict = {'2016': 512,
             '2017': 538,
             '2018': 486,
             '2019': 487,
             '2020': 317}

year_list = year_dict.keys()

for year_num in year_list:
    print("year: ", year_num)
    print(os.getcwd())
    os.listdir(os.path.join(os.getcwd(), year_num))
    try:
        with open('{}/updated_url_list.pkl'.format(year_num), 'rb') as f:
            updated_url_list = pickle.load(f)
        print("updated urls: ", len(updated_url_list))

        with open('{}/didnt_load.pkl'.format(year_num), 'rb') as f:
            didnt_load = pickle.load(f)
        print("didnt load pages: ", len(didnt_load))

        with open('{}/bade_pages.pkl'.format(year_num), 'rb') as f:
            bade_pages = pickle.load(f)
        print("bad pages: ", len(bade_pages))
    except:
        print("no files yet")

    with open('{}/first_url_list.pkl'.format(year_num), 'rb') as f:
        first_url_list = pickle.load(f)
    print("first urls pages: ", len(first_url_list))



# proj_url = 'https://handasa.ramat-gan.muni.il/newengine/Pages/request2.aspx#request/'
#
# print(first_url_list[:5])
#
# u_list = []
# for i in range(1, 5):
#     u_list.append(proj_url + year_num + str(i).zfill(5))
# print(u_list)