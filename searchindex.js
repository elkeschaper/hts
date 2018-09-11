Search.setIndex({docnames:["code_docs","config","contributors","data_transformations","docs","example_workflow","hit_selection","hts","hts.data_tasks","hts.plate","hts.plate_data","hts.protocol","hts.run","index","install","meta_data","model","modules"],envversion:53,filenames:["code_docs.rst","config.rst","contributors.rst","data_transformations.rst","docs.rst","example_workflow.rst","hit_selection.rst","hts.rst","hts.data_tasks.rst","hts.plate.rst","hts.plate_data.rst","hts.protocol.rst","hts.run.rst","index.rst","install.rst","meta_data.rst","model.rst","modules.rst"],objects:{"":{hts:[7,0,0,"-"]},"hts.conftest":{pytest_runtest_setup:[7,1,1,""]},"hts.data_tasks":{data_normalization:[8,0,0,"-"],data_tasks:[8,0,0,"-"],qc_detect_data_issues:[8,0,0,"-"],qc_knitr:[8,0,0,"-"],qc_matplotlib:[8,0,0,"-"]},"hts.data_tasks.data_normalization":{calculate_local_ssmd:[8,1,1,""],classify_by_cutoff:[8,1,1,""]},"hts.data_tasks.data_tasks":{perform_task:[8,1,1,""]},"hts.data_tasks.qc_detect_data_issues":{detect_low_cell_viability:[8,1,1,""]},"hts.data_tasks.qc_knitr":{chessboard_pattern:[8,1,1,""],compare_plate_replicates:[8,1,1,""],create_report:[8,1,1,""],dynamics:[8,1,1,""],heat_map:[8,1,1,""],heat_map_log10_mark_conditionally:[8,1,1,""],heat_map_mark_conditionally:[8,1,1,""],knitr_header_setup:[8,1,1,""],knitr_subset:[8,1,1,""],kolmogorov_smirnov:[8,1,1,""],kolmogorov_smirnov_estimated:[8,1,1,""],mean_value_across_plates:[8,1,1,""],perform_qc:[8,1,1,""],plate_layout:[8,1,1,""],replicate_correlation:[8,1,1,""],replicate_correlation_robust:[8,1,1,""],shapiro_wilk_normality_test:[8,1,1,""],smoothed_histogram:[8,1,1,""],smoothed_histogram_sample_type:[8,1,1,""],ssmd:[8,1,1,""],time_course:[8,1,1,""],wrap_knitr_chunk:[8,1,1,""],z_factor:[8,1,1,""],z_prime_factor:[8,1,1,""]},"hts.data_tasks.qc_matplotlib":{create_report:[8,1,1,""],heat_map_multiple:[8,1,1,""],heat_map_multiple_gaussian_process_model:[8,1,1,""],heat_map_single:[8,1,1,""],heat_map_single_gaussian_process_model:[8,1,1,""],slice_multiple_gaussian_process_model:[8,1,1,""],slice_single_gaussian_process_model:[8,1,1,""]},"hts.plate":{plate:[9,0,0,"-"]},"hts.plate.plate":{Plate:[9,2,1,""],translate_coordinate_humanreadable:[9,1,1,""],translate_humanreadable_coordinate:[9,1,1,""]},"hts.plate.plate.Plate":{__str__:[9,3,1,""],add_data:[9,3,1,""],calculate_control_normalized_signal:[9,3,1,""],calculate_linearly_normalized_signal:[9,3,1,""],calculate_local_ssmd:[9,3,1,""],calculate_net_fret:[9,3,1,""],calculate_normalization_by_division:[9,3,1,""],calculate_significance_compared_to_null_distribution:[9,3,1,""],classify_by_cutoff:[9,3,1,""],create:[9,3,1,""],cross_validate_predictions:[9,3,1,""],evaluate_well_value_prediction:[9,3,1,""],filter:[9,3,1,""],flatten_data:[9,3,1,""],flatten_values:[9,3,1,""],flatten_wells:[9,3,1,""],get_data_for_gaussian_process:[9,3,1,""],height:[9,4,1,""],map_coordinates:[9,3,1,""],name:[9,4,1,""],preprocess:[9,3,1,""],randomize_values:[9,3,1,""],subtract_readouts:[9,3,1,""],un_flatten_data:[9,3,1,""],width:[9,4,1,""],write:[9,3,1,""]},"hts.plate_data":{data_issue:[10,0,0,"-"],meta_data:[10,0,0,"-"],plate_data:[10,0,0,"-"],plate_data_io:[10,0,0,"-"],plate_layout:[10,0,0,"-"],readout:[10,0,0,"-"],readout_io:[10,0,0,"-"]},"hts.plate_data.data_issue":{DataIssue:[10,2,1,""]},"hts.plate_data.data_issue.DataIssue":{create_well_list:[10,5,1,""],layout_general_type:[10,4,1,""],sample_replicate_count:[10,4,1,""]},"hts.plate_data.meta_data":{MetaData:[10,2,1,""]},"hts.plate_data.plate_data":{PlateData:[10,2,1,""]},"hts.plate_data.plate_data.PlateData":{__iter__:[10,3,1,""],__str__:[10,3,1,""],add_data:[10,3,1,""],create:[10,5,1,""],create_csv:[10,5,1,""],create_excel:[10,5,1,""],create_excel_multiple_plates_per_file:[10,5,1,""],create_from_coordinate_tuple_dict:[10,5,1,""],create_pickle:[10,5,1,""],data:[10,4,1,""],get_data:[10,3,1,""],get_values:[10,3,1,""],get_wells:[10,3,1,""],height:[10,4,1,""],tags:[10,4,1,""],width:[10,4,1,""],write:[10,3,1,""]},"hts.plate_data.plate_data_io":{read_csv:[10,1,1,""],read_excel:[10,1,1,""]},"hts.plate_data.plate_layout":{PlateLayout:[10,2,1,""]},"hts.plate_data.plate_layout.PlateLayout":{create_csv:[10,5,1,""],invert:[10,3,1,""],layout_general_type:[10,4,1,""],sample_replicate_count:[10,4,1,""]},"hts.plate_data.readout":{Readout:[10,2,1,""]},"hts.plate_data.readout.Readout":{__str__:[10,3,1,""],create_envision_csv:[10,3,1,""],create_insulin_csv:[10,3,1,""],data:[10,4,1,""],height:[10,4,1,""],width:[10,4,1,""]},"hts.plate_data.readout_io":{read_envision_csv:[10,1,1,""],read_insulin_csv:[10,1,1,""]},"hts.protocol":{protocol:[11,0,0,"-"]},"hts.protocol.protocol":{Protocol:[11,2,1,""],ProtocolTask:[11,2,1,""]},"hts.protocol.protocol.Protocol":{create:[11,5,1,""],file:[11,4,1,""],get_tasks_by_tag:[11,3,1,""],name:[11,4,1,""],tasks:[11,4,1,""],write:[11,3,1,""]},"hts.protocol.protocol.ProtocolTask":{config:[11,4,1,""],create:[11,5,1,""],method:[11,4,1,""],name:[11,4,1,""],tags:[11,4,1,""],type:[11,4,1,""]},"hts.run":{constants:[12,0,0,"-"],run:[12,0,0,"-"],run_io:[12,0,0,"-"]},"hts.run.run":{Run:[12,2,1,""],merged_replicates:[12,1,1,""],send_mail:[12,1,1,""]},"hts.run.run.Run":{__iter__:[12,3,1,""],__str__:[12,3,1,""],_platelayout:[12,4,1,""],_protocol:[12,4,1,""],_qc:[12,4,1,""],add_data_from_data_frame:[12,3,1,""],add_meta_data:[12,3,1,""],analysis:[12,3,1,""],create:[12,5,1,""],create_from_config:[12,5,1,""],create_from_csv_file:[12,5,1,""],create_from_envision:[12,5,1,""],data_frame:[12,4,1,""],data_frame_samples:[12,4,1,""],do_task:[12,3,1,""],experimenter:[12,4,1,""],filter:[12,3,1,""],get_run_config_data:[12,3,1,""],gp_models:[12,4,1,""],height:[12,4,1,""],map_config_file_definition:[12,5,1,""],merger_add_data_from_data_frame:[12,3,1,""],merger_rank_samples:[12,3,1,""],merger_summarize_statistical_significance:[12,3,1,""],name:[12,4,1,""],net_qc:[12,4,1,""],plates:[12,4,1,""],preprocess:[12,3,1,""],protocol:[12,3,1,""],qc:[12,3,1,""],raw_qc:[12,4,1,""],width:[12,4,1,""],write:[12,3,1,""]},"hts.run.run_io":{add_meta_data:[12,1,1,""],column_plate_name:[12,4,1,""],column_well:[12,4,1,""],columns_metas:[12,4,1,""],columns_readouts:[12,4,1,""],convert_well_id_format:[12,1,1,""],delimiter:[12,4,1,""],file:[12,4,1,""],plate_layout_name:[12,4,1,""],plate_name:[12,4,1,""],read_csv:[12,1,1,""],readouts:[12,4,1,""],rename_pd_columns:[12,1,1,""],run:[12,4,1,""],serialize_as_csv_one_row_per_well:[12,1,1,""],serialize_as_pandas:[12,1,1,""],serialize_run_for_r:[12,1,1,""],well_name:[12,4,1,""]},hts:{conftest:[7,0,0,"-"],data_tasks:[8,0,0,"-"],plate:[9,0,0,"-"],plate_data:[10,0,0,"-"],protocol:[11,0,0,"-"],run:[12,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"],"5":["py","classmethod","Python class method"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:method","4":"py:attribute","5":"py:classmethod"},terms:{"414nm":9,"475nm":9,"525nm":9,"615nm":9,"665nm":9,"boolean":[8,9,12],"class":[9,10,11,12,13],"default":14,"export":10,"float":[8,9,12],"function":8,"import":[4,14],"int":[9,10,12],"new":8,"null":9,"return":[8,9,10,12],"true":[8,9,10,12],For:[8,9,14],HTS:[2,8,12,13,14],One:11,That:10,The:[2,4,9,10,11,12],There:1,With:14,Yes:10,__iter__:[10,12],__str__:[9,10,12],_platelayout:12,_protocol:12,_qc:12,_subplot:8,a001:12,abitrari:8,abov:8,acceptor:9,acceptor_:9,acceptor_channel:9,acceptor_fluorophor:9,access:14,accord:[9,12],aceptor:9,across:9,add:[9,10],add_data:[9,10],add_data_from_data_fram:12,add_meta_data:12,addit:13,address:12,adjust:10,adriano_conrad_aguzzi:12,advis:8,after:9,afterward:10,all:[1,4,8,9,10,11,12],allow:16,alongsid:16,alpha:8,also:[1,9,10],ambient:10,analysi:[0,1,7,12,13,16,17],apc:9,apertur:10,appli:8,arbitrari:[10,11,16],arg:[8,9,10,11,12],argument:12,arrai:10,arrang:10,assai:10,assayid:10,associ:9,assum:9,attach:12,auto:10,automat:4,avail:8,averag:9,axes:8,axesgrid:8,axessubplot:8,backbon:4,background:10,barcod:10,base:[1,8,9,10,11,12,13,16],basic:10,begin:10,below:9,better:9,bewar:1,binari:9,blank:9,bmg:10,bodi:12,bool:[9,12],both:[1,9],branch:4,buffer:9,buffer_:9,build:[10,16],calc:10,calcul:[9,10],calculate_control_normalized_sign:9,calculate_linearly_normalized_sign:9,calculate_local_ssmd:[8,9],calculate_net_fret:9,calculate_normalization_by_divis:9,calculate_significance_compared_to_null_distribut:9,can:[1,8,10,14,16],cdot:9,cell:8,cfp:9,chamber:10,channel:[9,10],channel_wise_info:10,channel_wise_read:10,check:[9,10,11,12],chessboard_pattern:8,chunk:8,chunk_nam:8,classif:9,classify_by_cutoff:[8,9],classmethod:[10,11,12],code:[4,8,13],col:10,collect:12,color:8,column:[10,12],column_nam:12,column_plate_nam:12,column_wel:12,columni:10,columns_meta:12,columns_readout:12,com:[12,14],combin:8,command:[4,14],common:8,compar:9,compare_plate_repl:8,compens:9,compli:8,compound:12,concaten:12,condit:[8,9,10],condition_data_tag:9,condition_data_typ:9,config:[10,11,12,13],config_data:[8,9],configobj:[1,11,12],configur:14,conform:[9,10],conftest:17,connect:[8,9,10,11,12,13],consid:8,constant:[0,7,14,17],contain:[8,10],content:[0,17],contributor:13,control:[1,8,9,10,12],control_readout_tag:8,control_sample_typ:8,controlled_sample_typ:8,convert_well_id_format:12,coordin:[9,10,12],coordinates_list:9,corner:10,correct:10,correspond:10,could:[8,9,12],cover:10,cps:10,creat:[8,9,10,11,12,14],create_csv:10,create_envision_csv:10,create_excel:10,create_excel_multiple_plates_per_fil:10,create_from_config:12,create_from_coordinate_tuple_dict:10,create_from_csv_fil:12,create_from_envis:12,create_insulin_csv:10,create_pickl:10,create_report:8,create_well_list:10,cross:9,cross_validate_predict:9,crosstalk:10,csv:[10,12],current:[8,9,10,11,12],cut:8,d_all:8,data:[1,8,9,10,12,13,16],data_0:12,data_1:12,data_fram:12,data_frame_sampl:12,data_issu:[0,7,17],data_issue_tag:8,data_load:8,data_norm:[0,7,17],data_predict:9,data_tag:[8,9,10],data_tag_classified_readout:9,data_tag_mean_neg:9,data_tag_mean_po:9,data_tag_normalized_readout:9,data_tag_p_valu:9,data_tag_randomized_readout:9,data_tag_readout:[8,9],data_tag_readout_differ:9,data_tag_readout_minuend:9,data_tag_readout_subtrahend:9,data_tag_ssmd:9,data_tag_standard_scor:9,data_tag_std_neg:9,data_tag_std_po:9,data_task:[0,7,17],data_typ:9,dataissu:10,dataset:9,date:[10,14],datum:10,debug:9,declar:8,defaultdatafold:10,defin:[1,8,9,10,11,12],degre:10,deinstal:14,delimit:[10,12],depend:9,describ:[9,10,11,12],descript:[8,10],design:16,detect:8,detect_low_cell_vi:8,develop:14,deviat:8,diamet:10,dict:[8,10,12],dictionari:8,dir:12,direct:10,directli:14,directori:[9,10,11,12],distribut:9,diverg:8,divis:9,do_task:12,document:13,doe:8,donor:9,donor_:9,donor_channel:9,donor_fluorophor:9,dynam:8,each:[8,10,12,13,16],easi:12,echo:8,edit:10,either:[8,9,12],elk:2,elkeschap:[4,14],elkewschap:12,els:[9,12],email_from:12,email_subject:12,email_to:12,emmenegg:2,end:10,environ:[4,8,14],envis:[10,12],equal:9,error:[9,10],estim:9,evalu:8,evaluate_well_value_predict:9,everyth:1,exactli:[10,11],exampl:[8,10],excel:10,exist:[8,12],expect:8,experi:[8,12],experiment:[10,12],explain:10,explicitli:8,express:[9,10],extract:[10,12],factor:9,factori:10,fall:9,fals:[8,9,12],field:10,file:[4,8,9,10,11,12,13],filenam:[10,12],filter:[8,9,12],filter_condit:12,finish:[10,12],first:4,fit:12,fixtur:9,flash:10,flatten:9,flatten_data:9,flatten_valu:9,flatten_wel:9,flow:16,fluoresc:10,fluorophor:9,fluorophore_acceptor:9,fluorophore_donor:9,fly:8,follow:[9,16],forc:[8,9,12],format:[1,9,10,11,12],formula:10,frame:[8,12],fret:9,from:[8,9,10,12,14],further:9,gaussian:[9,14],gener:10,georg:2,get:[9,10],get_data:[9,10],get_data_for_gaussian_process:9,get_run_config_data:12,get_tasks_by_tag:11,get_valu:10,get_wel:10,ggplot2:14,git:14,github:[4,13,14],given:10,glo:8,glucos:12,gmail:12,gp_model:12,gpy:14,gridextra:14,gripper:10,group:10,guex:2,hack:10,handl:16,has:9,hat:9,have:[8,9],header:8,heat_map:8,heat_map_log10_mark_condition:8,heat_map_mark_condition:8,heat_map_multipl:8,heat_map_multiple_gaussian_process_model:8,heat_map_singl:8,heat_map_single_gaussian_process_model:8,height:[9,10,12],here:1,high:[8,9,10,11,12,16],hint:4,hit:[13,16],html:[1,14],html_document:8,hts:[0,4,14],http:[1,4,14],humanread:9,humid:10,i_col:10,i_row:10,ignor:10,imag:16,implement:[8,12],implicitli:8,includ:[9,10,11],index:[0,4,10,13],indic:12,info:10,inform:[1,9,10,11,12,13,16],input:[9,10,11,12],instal:[4,10,13],instanc:[8,9,10,11,12],instead:[8,12,14],instrument:10,integr:8,intern:12,interpret:10,intro:13,introduc:[9,13],invert:10,ioanni:2,ipynb:1,is_higher_value_bett:9,is_twosid:9,issu:[8,10],item:7,iter:[10,12],its:10,itself:14,join:12,kei:[8,9,10],kernel_tag:8,kernel_typ:8,key_str:12,keyword:12,kinet:10,knit_html:8,knitr:[8,14],knitr_chunk_opt:8,knitr_header_setup:8,knitr_subset:8,knittr:8,known_data_typ:9,known_task_typ:11,kolmogorov_smirnov:8,kolmogorov_smirnov_estim:8,kwarg:[8,9,10,12],label:10,lambda:10,larg:10,last:10,latest:[1,14],layout:[9,10,12],layout_general_typ:10,letternumb:12,level:[8,10],like:1,line:[4,10,14,16],linearli:9,list:[8,9,10,11,12],load_data__tutori:1,loader:8,local:9,low:[8,9],lower:9,lum:10,luminesc:10,m32:8,m_insulinassay384:10,magnif:8,mai:[8,9,10,12],mail:12,make:[4,9,14],map:[9,10],map_config_file_definit:12,map_coordin:9,marc:2,markdown:8,mass:14,math:9,matplotlib:8,matric:10,matrix:10,mea:10,mean:9,mean_value_across_pl:8,measinfo:10,meastim:10,measur:[8,10,13],meisl:2,merg:12,merged_repl:12,merger_add_data_from_data_fram:12,merger_rank_sampl:12,merger_summarize_statistical_signific:12,messag:8,meta:[1,12,16],meta_data:[0,7,8,12,17],meta_data_exclude_column:12,meta_data_kwarg:12,meta_data_renam:12,meta_data_well_name_pattern:12,metadata:10,method:[8,9,10,11],method_nam:[8,9],methodnam:9,might:14,min:10,mind:16,misfortun:10,mode:10,model:[9,13,16],model_as_gaussian_process:8,modul:[13,17],more:13,move:10,mu_:9,multipl:[8,10,12],must:[1,10],n_max_iter:8,n_plate:12,n_plates_max:8,name:[1,8,9,10,11,12],necessari:[10,12],necessarili:11,need:[8,9,10,11,12],neg:[9,10],neg_k:10,negat:8,negative_control_kei:9,net:9,net_fret:9,net_fret_kei:9,net_qc:12,netfret:9,new_data_fram:8,next:14,nicknam:10,nicola:2,nomin:8,none:[8,9,10,11,12],nor:10,normal:[1,8,9,10,13,14,16],normalized_0:9,normalized_1:9,normalized__i:9,normalized_kei:9,normalizer_kei:9,note:10,notebook:1,now:14,number:[10,16],numpi:14,object:[9,10,11,12],off:8,omega:10,one:[8,10,11,12],onli:[4,8,9,10,11,12],oper:10,option:8,ordereddict:12,origin:[8,12],original_data_fram:8,other:[9,10],otherwis:9,our:4,out:10,output:[1,8,9,10,11,12],over:[10,12],packag:[0,14,17],page:[0,4,13],pair:9,panda:12,pandoc:14,param:9,paramet:[8,9,10,11,12],particular:10,pass:12,path:[1,8,9,10,11,12],path_data:8,path_knitr_data:8,pattern:9,pdf:14,per:[9,10,16],perform:[8,10,12],perform_qc:8,perform_task:8,perhap:8,pickl:[9,10,11,12],pip3:14,pip:14,place:10,plate:[0,7,8,10,12,16,17],plate_data:[0,7,9,17],plate_data_io:[0,7,17],plate_data_typ:12,plate_info:10,plate_layout:[0,7,8,9,17],plate_layout_nam:12,plate_nam:[8,12],plate_tag:8,platedata:[9,10],platelayout:[10,12],platemap:10,plot:8,plot_kwarg:8,plotli:8,pos:9,pos_control_lower_than_neg_control:9,pos_k:10,posit:[9,10],positive_control_kei:9,practic:8,predict:[0,7,17],preprocess:[9,12],preset:10,print:12,process:[9,14],program:10,project:[13,14],proportion:9,protocol:[0,7,10,12,17],protocoltask:[11,12],provid:8,publicli:10,purpos:9,push:4,pvalu:9,pypi:14,pytest_runtest_setup:7,python3:14,qc_detect_data_issu:[0,7,17],qc_knitr:[0,7,17],qc_matplotlib:[0,7,17],qc_report:[8,12],qualiti:[1,8,12],quality_control:8,qualitycontrol:12,rac:9,random:9,randomize_valu:9,randomized_sampl:9,raw:10,raw_qc:12,read:[10,12],read_csv:[10,12],read_envision_csv:10,read_excel:10,read_insulin_csv:10,readout:[0,7,8,9,12,16,17],readout_dict:9,readout_io:[0,7,17],readthedoc:1,real:8,realtim:8,recommend:14,redund:1,refer:[8,9,10],regard:8,relev:12,reload:12,remove_empty_row:[10,12],renam:[8,9],rename_columns_dict:12,rename_dict:12,rename_pd_column:12,repeat:10,replicate_correl:8,replicate_correlation_robust:8,replicate_defining_column:[8,12],report:[8,12,14],requir:[1,8,14],result:[8,9,10,12,16],result_fil:8,resultfile_tag:8,retriev:[9,10],return_list:9,return_str:[9,10,11,12],rewrit:9,rmarkdown:14,rotat:10,row:[10,12],rowi:10,rscript:14,run:[0,7,8,10,17],run_config:1,run_data:12,run_io:[0,7,17],s_k:10,same:[1,8,9,10,16],sampl:[8,9,10,13,16],sample_kei:[8,9],sample_replicate_count:10,sample_tag:[8,9],sample_tag_null_distribut:9,sample_typ:8,save:[1,9,12],scani:10,scanx:10,schaper:2,score:9,screen:[8,9,10,11,12,16],search:[0,13],see:[1,10],select:[13,16],self:[8,9,12],send_mail:12,separ:10,serial:[9,10,11,12],serialize_as_csv_one_row_per_wel:12,serialize_as_panda:12,serialize_run_for_r:12,set:[1,9,10,12],setter:8,setup:[8,9,14],sever:[9,12],shall:[10,12],shapiro_wilk_normality_test:8,sheet:10,sheffieldml:14,show:[9,10],signal:[9,10,12],signific:8,singl:[8,10,16],size:10,slice:8,slice_multiple_gaussian_process_model:8,slice_single_gaussian_process_model:8,slightli:1,smoothed_histogram:8,smoothed_histogram_sample_typ:8,smtp:12,smtp_port:12,smtp_server:12,smtp_usernam:12,snippet:14,soft:10,sourc:[7,8,9,10,11,12],specif:[1,8,9],specifi:[8,9,11,12],sphinx:4,spreadsheet:10,squar:9,ssmd:[8,9],standard:9,start:[4,10],state:[9,10,11,12],stefan:2,step:16,store:[9,16],str:[8,9,10,11,12],streamlin:13,string:[8,9,10,12],strong:8,structur:10,stuff:8,subclass:9,submodul:[0,17],subpackag:17,subset:[8,9],subset_requir:8,subtract_readout:9,suffer:8,suppli:8,suppos:9,sure:14,synopsi:[8,9,10,11,12],system:10,tabl:[8,10],tag:[8,9,10,11,12],taken:12,tale:10,task:[1,8,11,12],task_nam:8,temperatur:10,term:8,test:[10,16],thi:[1,4,8,9,10,11,12,13],threshold:[8,9],throughput:[8,9,10,11,12,16],time:[10,12,14],time_cours:8,timeglo:8,tip:4,titl:8,todo:[1,8],too:8,transform:13,translat:10,translate_coordinate_humanread:9,translate_humanreadable_coordin:9,truncat:8,tsv:12,tupl:[8,10,12],turn:10,two:1,type:[1,9,10,11,12],type_attribut:12,typic:9,un_flatten_data:9,undefin:10,under:14,unnorm:9,unnormalized_i:9,unnormalized_kei:9,updat:12,use:[1,4,9,10,12,14],used:[8,10,12],useful:[13,14],user:10,uses:14,using:[8,9,10,11,12],uslum:10,valid:9,valu:[8,9,10,12],value_data_tag:9,value_data_typ:9,value_str:12,value_typ:[9,10],verbos:8,version:[10,14],viabil:8,virtual:[4,14],visual:[8,9],visualis:8,vocabulari:10,wai:16,warn:[8,9,10],wdw:10,well:[8,9,10,12,16],well_list:10,well_nam:12,well_name_pattern:12,what:[1,9],when:[12,13],whenev:1,where:[9,10],whether:9,which:[4,8,9,10,12,14],white:8,who:2,width:[9,10,12],wise:9,within:[4,14],work:4,workon:4,workstat:10,would:[1,9],wrap_knitr_chunk:8,write:[9,10,11,12],x100:10,x101:10,x102:10,x103:10,x104:10,x105:10,x106:10,x107:10,x108:10,x109:10,x10:10,x110:10,x111:10,x112:10,x113:10,x114:10,x115:10,x116:10,x117:10,x118:10,x119:10,x11:10,x120:10,x121:10,x122:10,x123:10,x124:10,x125:10,x126:10,x127:10,x128:10,x129:10,x12:10,x130:10,x131:10,x132:10,x133:10,x134:10,x135:10,x136:10,x137:10,x138:10,x139:10,x13:10,x140:10,x141:10,x142:10,x143:10,x144:10,x145:10,x146:10,x147:10,x148:10,x149:10,x14:10,x150:10,x151:10,x152:10,x153:10,x154:10,x155:10,x156:10,x157:10,x158:10,x159:10,x15:10,x160:10,x161:10,x162:10,x163:10,x164:10,x165:10,x166:10,x167:10,x168:10,x169:10,x16:10,x170:10,x171:10,x172:10,x173:10,x174:10,x175:10,x176:10,x177:10,x178:10,x179:10,x17:10,x180:10,x181:10,x182:10,x183:10,x184:10,x185:10,x186:10,x187:10,x188:10,x189:10,x18:10,x190:10,x191:10,x192:10,x193:10,x194:10,x195:10,x196:10,x197:10,x198:10,x199:10,x19:10,x200:10,x201:10,x202:10,x203:10,x204:10,x205:10,x206:10,x207:10,x208:10,x209:10,x20:10,x210:10,x211:10,x212:10,x213:10,x214:10,x215:10,x216:10,x217:10,x218:10,x219:10,x21:10,x220:10,x221:10,x222:10,x223:10,x224:10,x225:10,x226:10,x227:10,x228:10,x229:10,x22:10,x230:10,x231:10,x232:10,x233:10,x234:10,x235:10,x236:10,x237:10,x238:10,x239:10,x23:10,x240:10,x241:10,x242:10,x243:10,x244:10,x245:10,x246:10,x247:10,x248:10,x249:10,x24:10,x250:10,x251:10,x252:10,x253:10,x254:10,x255:10,x256:10,x257:10,x258:10,x259:10,x25:10,x260:10,x261:10,x262:10,x263:10,x264:10,x265:10,x266:10,x267:10,x268:10,x269:10,x26:10,x270:10,x271:10,x272:10,x273:10,x274:10,x275:10,x276:10,x277:10,x278:10,x279:10,x27:10,x280:10,x281:10,x282:10,x283:10,x284:10,x285:10,x286:10,x287:10,x288:10,x289:10,x28:10,x290:10,x291:10,x292:10,x293:10,x294:10,x295:10,x296:10,x297:10,x298:10,x299:10,x29:10,x300:10,x301:10,x302:10,x303:10,x304:10,x305:10,x306:10,x307:10,x308:10,x309:10,x30:10,x310:10,x311:10,x312:10,x313:10,x314:10,x315:10,x316:10,x317:10,x318:10,x319:10,x31:10,x320:10,x321:10,x322:10,x323:10,x324:10,x325:10,x326:10,x327:10,x328:10,x329:10,x32:10,x330:10,x331:10,x332:10,x333:10,x334:10,x335:10,x336:10,x337:10,x338:10,x339:10,x33:10,x340:10,x341:10,x342:10,x343:10,x344:10,x345:10,x346:10,x347:10,x348:10,x349:10,x34:10,x350:10,x351:10,x352:10,x353:10,x354:10,x355:10,x356:10,x357:10,x358:10,x359:10,x35:10,x360:10,x361:10,x362:10,x363:10,x364:10,x365:10,x366:10,x367:10,x368:10,x369:10,x36:10,x370:10,x371:10,x372:10,x373:10,x374:10,x375:10,x376:10,x377:10,x378:10,x379:10,x37:10,x380:10,x381:10,x382:10,x383:10,x384:10,x38:10,x39:10,x40:10,x41:10,x42:10,x43:10,x44:10,x45:10,x46:10,x47:10,x48:10,x49:10,x50:10,x51:10,x52:10,x53:10,x54:10,x55:10,x56:10,x57:10,x58:10,x59:10,x60:10,x61:10,x62:10,x63:10,x64:10,x65:10,x66:10,x67:10,x68:10,x69:10,x70:10,x71:10,x72:10,x73:10,x74:10,x75:10,x76:10,x77:10,x78:10,x79:10,x80:10,x81:10,x82:10,x83:10,x84:10,x85:10,x86:10,x87:10,x88:10,x89:10,x90:10,x91:10,x92:10,x93:10,x94:10,x95:10,x96:10,x97:10,x98:10,x99:10,x_high:9,x_low:9,xenario:2,xyz005:12,yet:8,yfp:9,you:[1,14],your:[1,4,14],z_factor:8,z_prime_factor:8,zoller:2},titles:["Modules","HTS configuration files","Contributors &amp; Background","High-througput screening data transformations","Docs","Example workflow","Hit Selection","hts package","hts.data_tasks package","hts.plate package","hts.plate_data package","hts.protocol package","hts.run package","High Throughput Screening Library - beta version","Installation","Connecting screen data with information on the samples","When HTS is useful \u2026","hts"],titleterms:{"new":4,HTS:[1,16],analysi:8,background:[2,13],beta:13,config:1,configur:[1,13],conftest:7,connect:15,constant:12,content:[7,8,9,10,11,12],contributor:2,data:[3,15],data_issu:10,data_norm:8,data_task:8,deploi:4,doc:4,exampl:5,file:1,from:4,gener:4,high:[3,13],hit:6,html:4,hts:[7,8,9,10,11,12,17],indic:[0,13],inform:15,instal:14,librari:13,meta_data:10,modul:[0,7,8,9,10,11,12],outdat:13,packag:[7,8,9,10,11,12],peopl:2,plate:9,plate_data:10,plate_data_io:10,plate_layout:10,predict:9,protocol:[1,11],qc_detect_data_issu:8,qc_knitr:8,qc_matplotlib:8,readout:10,readout_io:10,rst:4,run:[1,12],run_io:12,sampl:15,screen:[3,13,15],select:6,submodul:[7,8,9,10,11,12],subpackag:7,tabl:[0,13],task:13,throughput:13,througput:3,todo:[9,10,11,12],transform:3,tutori:13,useful:16,version:13,when:16,workflow:5}})