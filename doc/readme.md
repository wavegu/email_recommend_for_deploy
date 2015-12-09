# email推荐系统

##代码管理
* git remote add origin https://wavegu@bitbucket.org/email\_recommender/email\_recommender.git

##输入
* json格式
* [{'name': 'Eric', 'affiliation': 'Tsinghua University'}]

##输出
* json格式
	* [{'name': 'Eric', 'affiliation': 'Tsinghua University', 'email_list': ['eric@126.com', 'eric@163.com']}]
* csv格式
	* name, affiliation, email1, email2, email3...

##模块
* searcher
	* 输入：email\_recommender/resource/input\_person_list
		* [{'name': 'Eric', 'affiliation': 'Tsinghua University'}]
	* 输出：
		* email\_recommender/by\_product/google\_page文件夹
		* email\_recommender/by\_product/google\_item文件夹，以人名为单位生成name.json
			* [{'title', 'content', 'cite\_url', 'cite_name'}, {}]
		* 流程：
			* 爬取google结果，得到email\_recommender/by\_product/google\_page文件夹
			* 用google\_html_parser.py进行feed，得到email\_recommender/by\_product/google\_item文件夹
	
* classifier
	* 输入：email\_recommender/by\_product/google\_item文件夹
	* 输出：email\_recommender/result/recommend_result.json
		* [{'name', 'affiliation', 'email_list'}]
	* 流程：
		* 对email\_recommender/by\_product/google\_item文件夹中的每一个人json生成email的feature文件
		* 用svm进行classify
		* parse输出结果，判断正负
		* 正例加入email_list(这里可以设置阈值，通过放宽和锁紧阈值来调整正例判断的依据)
		* email\_recommender/result/recommend_result.json

