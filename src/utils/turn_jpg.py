# -*- coding: utf-8 -*-
import maplab
 
# 加载pbstream文件
pbstream_filepath = '/home/robuster/Downloads/mymap.pbstream'
map_folder = '/home/robuster/Downloads'  # 输出文件夹
 
# 创建地图实例
localization_map_folder = map_folder
localization_map_filename = 'localization_map'
 
# 加载pbstream文件到地图实例
localization_map = maplab.LocalizationMap.load_from_file(
    localization_map_folder, localization_map_filename, pbstream_filepath)
 
# 获取地图的深度图
depth_image = localization_map.get_depth_image()
 
# 将深度图保存为JPG文件
jpg_filename = 'localization_map.jpg'
maplab.image_utils.save_image_as_jpg(depth_image, map_folder, jpg_filename)