# -*- coding: utf-8 -*-
import json  # noqa: F401
import os  # noqa: F401
import time
import unittest
from configparser import ConfigParser  # py3
from os import environ

from installed_clients.WorkspaceClient import Workspace as workspaceService
from kb_blast.authclient import KBaseAuth as _KBaseAuth
from kb_blast.kb_blastImpl import kb_blast
from kb_blast.kb_blastServer import MethodContext


class kb_blastTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_blast'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_blast',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_blast(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_blast_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    #
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    #


    # Test BLASTn
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_BLASTn_Search_01")
    def test_kb_blast_BLASTn_Search_01(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods

        obj_basename = 'BLASTn'
        obj_out_name = obj_basename+".test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_001566335.1/1'  # E. coli K-12 MG1655

        # E. coli K-12 MG1655 dnaA
        query_seq_nuc = 'GTGTCACTTTCGCTTTGGCAGCAGTGTCTTGCCCGATTGCAGGATGAGTTACCAGCCACAGAATTCAGTATGTGGATACGCCCATTGCAGGCGGAACTGAGCGATAACACGCTGGCCCTGTACGCGCCAAACCGTTTTGTCCTCGATTGGGTACGGGACAAGTACCTTAATAATATCAATGGACTGCTAACCAGTTTCTGCGGAGCGGATGCCCCACAGCTGCGTTTTGAAGTCGGCACCAAACCGGTGACGCAAACGCCACAAGCGGCAGTGACGAGCAACGTCGCGGCCCCTGCACAGGTGGCGCAAACGCAGCCGCAACGTGCTGCGCCTTCTACGCGCTCAGGTTGGGATAACGTCCCGGCCCCGGCAGAACCGACCTATCGTTCTAACGTAAACGTCAAACACACGTTTGATAACTTCGTTGAAGGTAAATCTAACCAACTGGCGCGCGCGGCGGCTCGCCAGGTGGCGGATAACCCTGGCGGTGCCTATAACCCGTTGTTCCTTTATGGCGGCACGGGTCTGGGTAAAACTCACCTGCTGCATGCGGTGGGTAACGGCATTATGGCGCGCAAGCCGAATGCCAAAGTGGTTTATATGCACTCCGAGCGCTTTGTTCAGGACATGGTTAAAGCCCTGCAAAACAACGCGATCGAAGAGTTTAAACGCTACTACCGTTCCGTAGATGCACTGCTGATCGACGATATTCAGTTTTTTGCTAATAAAGAACGATCTCAGGAAGAGTTTTTCCACACCTTCAACGCCCTGCTGGAAGGTAATCAACAGATCATTCTCACCTCGGATCGCTATCCGAAAGAGATCAACGGCGTTGAGGATCGTTTGAAATCCCGCTTCGGTTGGGGACTGACTGTGGCGATCGAACCGCCAGAGCTGGAAACCCGTGTGGCGATCCTGATGAAAAAGGCCGACGAAAACGACATTCGTTTGCCGGGCGAAGTGGCGTTCTTTATCGCCAAGCGTCTACGATCTAACGTACGTGAGCTGGAAGGGGCGCTGAACCGCGTCATTGCCAATGCCAACTTTACCGGACGGGCGATCACCATCGACTTCGTGCGTGAGGCGCTGCGCGACTTGCTGGCATTGCAGGAAAAACTGGTCACCATCGACAATATTCAGAAGACGGTGGCGGAGTACTACAAGATCAAAGTCGCGGATCTCCTTTCCAAGCGTCGATCCCGCTCGGTGGCGCGTCCGCGCCAGATGGCGATGGCGCTGGCGAAAGAGCTGACTAACCACAGTCTGCCGGAGATTGGCGATGCGTTTGGTGGCCGTGACCACACGACGGTGCTTCATGCCTGCCGTAAGATCGAGCAGTTGCGTGAAGAGAGCCACGATATCAAAGAAGATTTTTCAAATTTAATCAGAACATTGTCATCGTAA'

        parameters = { 'workspace_name': self.getWsName(),
                       'input_one_sequence': query_seq_nuc,
                       #'input_one_ref': "",
                       'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "97.0",
                       'overlap_fraction': "50.0",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().BLASTn_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Test BLASTp
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_BLASTp_Search_01")
    def test_kb_blast_BLASTp_Search_01(self):
        obj_basename = 'BLASTp'
        obj_out_name = obj_basename+".test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_001566335.1/1'  # E. coli K-12 MG1655

        # E. coli K-12 MG1655 dnaA
        query_seq_prot = 'MSLSLWQQCLARLQDELPATEFSMWIRPLQAELSDNTLALYAPNRFVLDWVRDKYLNNINGLLTSFCGADAPQLRFEVGTKPVTQTPQAAVTSNVAAPAQVAQTQPQRAAPSTRSGWDNVPAPAEPTYRSNVNVKHTFDNFVEGKSNQLARAAARQVADNPGGAYNPLFLYGGTGLGKTHLLHAVGNGIMARKPNAKVVYMHSERFVQDMVKALQNNAIEEFKRYYRSVDALLIDDIQFFANKERSQEEFFHTFNALLEGNQQIILTSDRYPKEINGVEDRLKSRFGWGLTVAIEPPELETRVAILMKKADENDIRLPGEVAFFIAKRLRSNVRELEGALNRVIANANFTGRAITIDFVREALRDLLALQEKLVTIDNIQKTVAEYYKIKVADLLSKRRSRSVARPRQMAMALAKELTNHSLPEIGDAFGGRDHTTVLHACRKIEQLREESHDIKEDFSNLIRTLSS'
        
        parameters = { 'workspace_name': self.getWsName(),
                       'input_one_sequence': query_seq_prot,
                       #'input_one_ref': "",
                       'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "40.0",
                       'overlap_fraction': "50.0",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().BLASTp_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Test BLASTx
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_BLASTx_Search_01")
    def test_kb_blast_BLASTx_Search_01(self):
        obj_basename = 'BLASTx'
        obj_out_name = obj_basename+'.'+"test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_001566335.1/1'  # E. coli K-12 MG1655

        # E. coli K-12 MG1655 dnaA
        query_seq_nuc = 'GTGTCACTTTCGCTTTGGCAGCAGTGTCTTGCCCGATTGCAGGATGAGTTACCAGCCACAGAATTCAGTATGTGGATACGCCCATTGCAGGCGGAACTGAGCGATAACACGCTGGCCCTGTACGCGCCAAACCGTTTTGTCCTCGATTGGGTACGGGACAAGTACCTTAATAATATCAATGGACTGCTAACCAGTTTCTGCGGAGCGGATGCCCCACAGCTGCGTTTTGAAGTCGGCACCAAACCGGTGACGCAAACGCCACAAGCGGCAGTGACGAGCAACGTCGCGGCCCCTGCACAGGTGGCGCAAACGCAGCCGCAACGTGCTGCGCCTTCTACGCGCTCAGGTTGGGATAACGTCCCGGCCCCGGCAGAACCGACCTATCGTTCTAACGTAAACGTCAAACACACGTTTGATAACTTCGTTGAAGGTAAATCTAACCAACTGGCGCGCGCGGCGGCTCGCCAGGTGGCGGATAACCCTGGCGGTGCCTATAACCCGTTGTTCCTTTATGGCGGCACGGGTCTGGGTAAAACTCACCTGCTGCATGCGGTGGGTAACGGCATTATGGCGCGCAAGCCGAATGCCAAAGTGGTTTATATGCACTCCGAGCGCTTTGTTCAGGACATGGTTAAAGCCCTGCAAAACAACGCGATCGAAGAGTTTAAACGCTACTACCGTTCCGTAGATGCACTGCTGATCGACGATATTCAGTTTTTTGCTAATAAAGAACGATCTCAGGAAGAGTTTTTCCACACCTTCAACGCCCTGCTGGAAGGTAATCAACAGATCATTCTCACCTCGGATCGCTATCCGAAAGAGATCAACGGCGTTGAGGATCGTTTGAAATCCCGCTTCGGTTGGGGACTGACTGTGGCGATCGAACCGCCAGAGCTGGAAACCCGTGTGGCGATCCTGATGAAAAAGGCCGACGAAAACGACATTCGTTTGCCGGGCGAAGTGGCGTTCTTTATCGCCAAGCGTCTACGATCTAACGTACGTGAGCTGGAAGGGGCGCTGAACCGCGTCATTGCCAATGCCAACTTTACCGGACGGGCGATCACCATCGACTTCGTGCGTGAGGCGCTGCGCGACTTGCTGGCATTGCAGGAAAAACTGGTCACCATCGACAATATTCAGAAGACGGTGGCGGAGTACTACAAGATCAAAGTCGCGGATCTCCTTTCCAAGCGTCGATCCCGCTCGGTGGCGCGTCCGCGCCAGATGGCGATGGCGCTGGCGAAAGAGCTGACTAACCACAGTCTGCCGGAGATTGGCGATGCGTTTGGTGGCCGTGACCACACGACGGTGCTTCATGCCTGCCGTAAGATCGAGCAGTTGCGTGAAGAGAGCCACGATATCAAAGAAGATTTTTCAAATTTAATCAGAACATTGTCATCGTAA'

        parameters = { 'workspace_name': self.getWsName(),
                       'input_one_sequence': query_seq_nuc,
                       #'input_one_ref': "",
                       'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "40.0",
                       'overlap_fraction': "50.0",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().BLASTx_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Test tBLASTx
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_tBLASTx_Search_01")
    def test_kb_blast_tBLASTx_Search_01(self):
        obj_basename = 'tBLASTx'
        obj_out_name = obj_basename+'.'+"test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_001566335.1/1'  # E. coli K-12 MG1655

        # E. coli K-12 MG1655 dnaA
        query_seq_nuc = 'GTGTCACTTTCGCTTTGGCAGCAGTGTCTTGCCCGATTGCAGGATGAGTTACCAGCCACAGAATTCAGTATGTGGATACGCCCATTGCAGGCGGAACTGAGCGATAACACGCTGGCCCTGTACGCGCCAAACCGTTTTGTCCTCGATTGGGTACGGGACAAGTACCTTAATAATATCAATGGACTGCTAACCAGTTTCTGCGGAGCGGATGCCCCACAGCTGCGTTTTGAAGTCGGCACCAAACCGGTGACGCAAACGCCACAAGCGGCAGTGACGAGCAACGTCGCGGCCCCTGCACAGGTGGCGCAAACGCAGCCGCAACGTGCTGCGCCTTCTACGCGCTCAGGTTGGGATAACGTCCCGGCCCCGGCAGAACCGACCTATCGTTCTAACGTAAACGTCAAACACACGTTTGATAACTTCGTTGAAGGTAAATCTAACCAACTGGCGCGCGCGGCGGCTCGCCAGGTGGCGGATAACCCTGGCGGTGCCTATAACCCGTTGTTCCTTTATGGCGGCACGGGTCTGGGTAAAACTCACCTGCTGCATGCGGTGGGTAACGGCATTATGGCGCGCAAGCCGAATGCCAAAGTGGTTTATATGCACTCCGAGCGCTTTGTTCAGGACATGGTTAAAGCCCTGCAAAACAACGCGATCGAAGAGTTTAAACGCTACTACCGTTCCGTAGATGCACTGCTGATCGACGATATTCAGTTTTTTGCTAATAAAGAACGATCTCAGGAAGAGTTTTTCCACACCTTCAACGCCCTGCTGGAAGGTAATCAACAGATCATTCTCACCTCGGATCGCTATCCGAAAGAGATCAACGGCGTTGAGGATCGTTTGAAATCCCGCTTCGGTTGGGGACTGACTGTGGCGATCGAACCGCCAGAGCTGGAAACCCGTGTGGCGATCCTGATGAAAAAGGCCGACGAAAACGACATTCGTTTGCCGGGCGAAGTGGCGTTCTTTATCGCCAAGCGTCTACGATCTAACGTACGTGAGCTGGAAGGGGCGCTGAACCGCGTCATTGCCAATGCCAACTTTACCGGACGGGCGATCACCATCGACTTCGTGCGTGAGGCGCTGCGCGACTTGCTGGCATTGCAGGAAAAACTGGTCACCATCGACAATATTCAGAAGACGGTGGCGGAGTACTACAAGATCAAAGTCGCGGATCTCCTTTCCAAGCGTCGATCCCGCTCGGTGGCGCGTCCGCGCCAGATGGCGATGGCGCTGGCGAAAGAGCTGACTAACCACAGTCTGCCGGAGATTGGCGATGCGTTTGGTGGCCGTGACCACACGACGGTGCTTCATGCCTGCCGTAAGATCGAGCAGTTGCGTGAAGAGAGCCACGATATCAAAGAAGATTTTTCAAATTTAATCAGAACATTGTCATCGTAA'

        parameters = { 'workspace_name': self.getWsName(),
                       'input_one_sequence': query_seq_nuc,
                       #'input_one_ref': "",
                       'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "40",
                       'overlap_fraction': "50",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().tBLASTx_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Test tBLASTn
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_tBLASTn_Search_01")
    def test_kb_blast_tBLASTn_Search_01(self):
        obj_basename = 'tBLASTn'
        obj_out_name = obj_basename+'.'+"test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_001566335.1/1'  # E. coli K-12 MG1655

        # E. coli K-12 MG1655 dnaA
        query_seq_prot = 'MSLSLWQQCLARLQDELPATEFSMWIRPLQAELSDNTLALYAPNRFVLDWVRDKYLNNINGLLTSFCGADAPQLRFEVGTKPVTQTPQAAVTSNVAAPAQVAQTQPQRAAPSTRSGWDNVPAPAEPTYRSNVNVKHTFDNFVEGKSNQLARAAARQVADNPGGAYNPLFLYGGTGLGKTHLLHAVGNGIMARKPNAKVVYMHSERFVQDMVKALQNNAIEEFKRYYRSVDALLIDDIQFFANKERSQEEFFHTFNALLEGNQQIILTSDRYPKEINGVEDRLKSRFGWGLTVAIEPPELETRVAILMKKADENDIRLPGEVAFFIAKRLRSNVRELEGALNRVIANANFTGRAITIDFVREALRDLLALQEKLVTIDNIQKTVAEYYKIKVADLLSKRRSRSVARPRQMAMALAKELTNHSLPEIGDAFGGRDHTTVLHACRKIEQLREESHDIKEDFSNLIRTLSS'
        
        parameters = { 'workspace_name': self.getWsName(),
                       'input_one_sequence': query_seq_prot,
                       #'input_one_ref': "",
                       'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "40",
                       'overlap_fraction': "50",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().tBLASTn_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Test psiBLAST
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_psiBLAST_msa_start_Search_01")
    def test_kb_blast_psiBLAST_msa_start_Search_01(self):
        obj_basename = 'psiBLAST_msa_start'
        obj_out_name = obj_basename+'.'+"test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'

        # MSA
        MSA_json_file = os.path.join('data', 'DsrA.MSA.json')
        with open (MSA_json_file, 'r') as MSA_json_fh:
            MSA_obj = json.load(MSA_json_fh)

        provenance = [{}]
        MSA_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        MSA_ref = str(MSA_info[WSID_I])+'/'+str(MSA_info[OBJID_I])+'/'+str(MSA_info[VERSION_I])

        
        parameters = { 'workspace_name': self.getWsName(),
                       #'input_one_sequence': "",
                       #'input_one_ref': "",
                       'input_msa_ref': MSA_ref,
                       #'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "10",
                       'overlap_fraction': "50",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().psiBLAST_msa_start_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertIsNotNone(report_obj['objects_created'][0]['ref'])

        created_obj_0_info = self.getWsClient().get_object_info_new({'objects':[{'ref':report_obj['objects_created'][0]['ref']}]})[0]
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        self.assertEqual(created_obj_0_info[NAME_I], obj_out_name)
        self.assertEqual(created_obj_0_info[TYPE_I].split('-')[0], obj_out_type)
        pass


    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_kb_blast_psiBLAST_msa_start_Search_02_nuc_MSA")
    def test_kb_blast_psiBLAST_msa_start_Search_02_nuc_MSA(self):
        obj_basename = 'psiBLAST_msa_start'
        obj_out_name = obj_basename+'.'+"test_output.FS"
        obj_out_type = "KBaseCollections.FeatureSet"

        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = 'ReferenceDataManager/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'

        # MSA
        MSA_json_file = os.path.join('data', 'ExbD_nuc.MSA.json')
        with open (MSA_json_file, 'r') as MSA_json_fh:
            MSA_obj = json.load(MSA_json_fh)

        provenance = [{}]
        MSA_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_nuc',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple
        MSA_ref = str(MSA_info[WSID_I])+'/'+str(MSA_info[OBJID_I])+'/'+str(MSA_info[VERSION_I])

        
        parameters = { 'workspace_name': self.getWsName(),
                       #'input_one_sequence': "",
                       #'input_one_ref': "",
                       'input_msa_ref': MSA_ref,
                       #'output_one_name': obj_basename+'.'+"test_query.SS",
                       'input_many_ref': genome_ref_1,
                       'output_filtered_name': obj_out_name,
                       'e_value': ".001",
                       'bitscore': "50",
                       'ident_thresh': "10",
                       'overlap_fraction': "50",
                       'maxaccepts': "1000",
                       'output_extra_format': "none"
                     }

        ret = self.getImpl().psiBLAST_msa_start_Search(self.getContext(), parameters)[0]
        self.assertIsNotNone(ret['report_ref'])

        # check created obj
        #report_obj = self.getWsClient().get_objects2({'objects':[{'ref':ret['report_ref']}]})[0]['data']
        report_obj = self.getWsClient().get_objects([{'ref':ret['report_ref']}])[0]['data']
        self.assertEqual(report_obj['text_message'][0:7],"FAILURE")
        pass
