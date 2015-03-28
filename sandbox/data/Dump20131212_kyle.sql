CREATE DATABASE  IF NOT EXISTS `pad` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `pad`;
-- MySQL dump 10.13  Distrib 5.5.29, for debian-linux-gnu (x86_64)
--
-- Host: kyle    Database: pad
-- ------------------------------------------------------
-- Server version	5.5.29-0ubuntu0.12.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `scale`
--

DROP TABLE IF EXISTS `scale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scale` (
  `time` double NOT NULL DEFAULT '0',
  `sensor` char(20) NOT NULL DEFAULT '',
  `x_scale` double DEFAULT NULL,
  `y_scale` double DEFAULT NULL,
  `z_scale` double DEFAULT NULL,
  PRIMARY KEY (`time`,`sensor`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scale`
--

LOCK TABLES `scale` WRITE;
/*!40000 ALTER TABLE `scale` DISABLE KEYS */;
INSERT INTO `scale` VALUES (988747200,'hirap',1,1,1),(988754400,'oss',1,1,1),(991658050,'121f06',1,1,1),(991658051,'121f05',1,1,1),(991658052,'121f04',1,1,1),(991658053,'121f03',1,1,1),(991658054,'121f02',1,1,1),(1078236000,'es13',1,1,1),(1078240800,'es13',1,1,1),(1094947200,'es02',1,1,1);
/*!40000 ALTER TABLE `scale` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `iss_config`
--

DROP TABLE IF EXISTS `iss_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iss_config` (
  `time` double NOT NULL DEFAULT '0',
  `iss_config` text,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `iss_config`
--

LOCK TABLES `iss_config` WRITE;
/*!40000 ALTER TABLE `iss_config` DISABLE KEYS */;
INSERT INTO `iss_config` VALUES (975675600,'Increment: 2, Flight: 6A'),(988749145,'Increment: 2, Flight: 6A'),(995757051,'Increment: 2, Flight: 7A'),(998319129,'Increment: 3, Flight: 7A.1'),(1008365907,'Increment: 4, Flight: UF1'),(1019044782,'Increment: 4, Flight: 8A'),(1034774151,'Increment: 5, Flight: 9A'),(1023969600,'Increment: 5, Flight: UF2'),(1038853800,'Increment: 6, Flight: 11A'),(1051509360,'Increment: 7, Flight: 6S'),(1067296680,'Increment: 8, Flight: 7S'),(1098565920,'Increment: 10, Flight: 9S'),(1083271920,'Increment: 9, Flight: 8S'),(1114368600,'Increment: 11, Flight: 10S'),(1128980400,'Increment: 12, Flight: 11S'),(1144528200,'Increment: 13, Flight: 12S'),(1158497400,'Increment: 13, Flight 12A'),(1159480200,'Increment: 14, Flight: 13S'),(1166463339,'Increment: 14, Flight: 12A.1'),(1224806457,'Increment: 18, Flight: 17S'),(1217548800,'Increment: 17, Flight: 1J'),(1227916800,'Increment: 18, Flight: ULF2'),(1239062400,'Increment: 19, Flight: 15A'),(1311638400,'Increment:  28, Flight: ULF7'),(1297123200,'Increment:  26, Flight: UF5');
/*!40000 ALTER TABLE `iss_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dqm`
--

DROP TABLE IF EXISTS `dqm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dqm` (
  `time` double NOT NULL DEFAULT '0',
  `sensor` varchar(20) NOT NULL DEFAULT '',
  `dqm` text,
  PRIMARY KEY (`time`,`sensor`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dqm`
--

LOCK TABLES `dqm` WRITE;
/*!40000 ALTER TABLE `dqm` DISABLE KEYS */;
INSERT INTO `dqm` VALUES (988711200,'oss','Valid'),(988714800,'hirap','Valid'),(991657906,'121f05','Valid'),(991657901,'121f06','Valid '),(991657902,'121f02','Valid '),(991657904,'121f03','Valid'),(991657905,'121f04','Valid'),(996686899,'oss','Bias Calib. Disabled'),(998686016,'oss','Valid'),(1026324503,'121f08','Valid '),(1026324504,'ossbtmf','Valid'),(1026324504,'ossfbias','Valid '),(1026324504,'ossraw','Valid '),(1041841800,'121f02','Valid'),(1041853800,'121f02','Valid'),(1042731541,'radgse','Valid'),(1061301600,'hirap','HiRAP timing errors exist; Current HiRAP time ahead of realtime by 48 seconds; Contact pimsops@grc.nasa.gov for details'),(1061891268,'hirap','HiRAP timing errors exist; Current HiRAP time ahead of realtime by 65 seconds; Contact pimsops@grc.nasa.gov for details'),(1062169765,'hirap','HiRAP timing errors exist; Current HiRAP time ahead of realtime by 72 seconds; Contact pimsops@grc.nasa.gov for details'),(1062507973,'hirap','HiRAP timing errors exist; Current HiRAP time ahead of realtime by 83 seconds; Contact pimsops@grc.nasa.gov for details'),(1063377095,'hirap','HiRAP timing errors exist; Current HiRAP time ahead of realtime by 106 seconds; Contact pimsops@grc.nasa.gov for details'),(1066996800,'hirap','Valid'),(1066996801,'hirap','Valid.  HiRAP timing correction started on GMT 24-Oct-2003.'),(1078240800,'es13','Valid'),(1078236000,'es13','Valid'),(1080834660,'oss','gimbal investigation, gimbals rotated'),(1080834660,'ossbtmf','gimbal investigation, gimbals rotated'),(1080834660,'ossraw','gimbal investigation, gimbals rotated'),(1080835260,'ossraw','Valid'),(1080835260,'oss','Valid'),(1080835260,'ossbtmf','Valid'),(1095604018,'oss','120Hz Investigation - IG at Opposite'),(1095604018,'ossbtmf','120 Hz Investigation - IG at Opposite'),(1095604018,'ossraw','120Hz Investigation - IG at Opposite'),(1095773880,'ossraw','Valid'),(1095773880,'oss','Valid'),(1095773880,'ossbtmf','Valid'),(1094947200,'es02','Valid');
/*!40000 ALTER TABLE `dqm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expected_config`
--

DROP TABLE IF EXISTS `expected_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expected_config` (
  `time` double NOT NULL DEFAULT '0',
  `sensor` char(20) NOT NULL DEFAULT '',
  `rate` double DEFAULT NULL COMMENT 'this is how the sample rate (in sa/sec) is referenced in packet headers according to packetWriter.py code',
  PRIMARY KEY (`time`,`sensor`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC COMMENT='used to inspect packets (via embellished packetWriter.py cod';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expected_config`
--

LOCK TABLES `expected_config` WRITE;
/*!40000 ALTER TABLE `expected_config` DISABLE KEYS */;
INSERT INTO `expected_config` VALUES (1325275631,'121f03',500),(1325275632,'es06',500),(1386853310,'121f05',500);
/*!40000 ALTER TABLE `expected_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bias`
--

DROP TABLE IF EXISTS `bias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bias` (
  `time` double NOT NULL DEFAULT '0',
  `sensor` text,
  `x_bias` double DEFAULT NULL,
  `y_bias` double DEFAULT NULL,
  `z_bias` double DEFAULT NULL,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bias`
--

LOCK TABLES `bias` WRITE;
/*!40000 ALTER TABLE `bias` DISABLE KEYS */;
INSERT INTO `bias` VALUES (975675602,'121f05',1.23,4.46,7.89),(975675603,'121f04',1.23,4.46,7.89),(975675600,'hirap',99.99,99.99,99.99),(975675601,'121f06',1.23,4.46,7.89),(975675604,'121f03',1.23,4.46,7.89),(975675605,'121f02',1.23,4.46,7.89),(1078236000,'es13',1,2,3),(1078240800,'es13',1,1,1),(1094947200,'es02',0,0,0);
/*!40000 ALTER TABLE `bias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coord_system_db`
--

DROP TABLE IF EXISTS `coord_system_db`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coord_system_db` (
  `time` double NOT NULL DEFAULT '0',
  `coord_name` varchar(20) NOT NULL DEFAULT '',
  `r_orient` double DEFAULT NULL,
  `p_orient` double DEFAULT NULL,
  `y_orient` double DEFAULT NULL,
  `x_location` double DEFAULT NULL,
  `y_location` double DEFAULT NULL,
  `z_location` double DEFAULT NULL,
  `location_name` text,
  PRIMARY KEY (`time`,`coord_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coord_system_db`
--

LOCK TABLES `coord_system_db` WRITE;
/*!40000 ALTER TABLE `coord_system_db` DISABLE KEYS */;
INSERT INTO `coord_system_db` VALUES (988675200,'SSAnalysis',0,0,0,0,0,0,'S0, Geom. Ctr. ITA'),(990112364,'121f04',0,30,-90,149.54,-40.54,135.25,'LAB1O2, ER1, Lower Z Panel'),(988678800,'hirap',180,0,0,138.68,-16.18,142.35,'LAB1O2, ER1, Lockers 3,4'),(988682400,'oss',90,0,0,135.28,-10.68,132.12,'LAB1O2, ER1, Lockers 3,4'),(1243209600,'121f02',180,-45,0,455.55,-227.69,229.07,'JPM1F3, TCQ, Lower Panel'),(990112303,'121f03',0,30,-90,191.54,-40.54,135.25,'LAB1O1, ER2, Lower Z Panel'),(990112480,'121f05',90,0,90,185.17,38.55,149.93,'LAB1O1, ER2, Upper Z Panel'),(990805113,'121f02',-90,0,-90,128.73,-23.53,144.15,'LAB1O2, ER1, Drawer 1'),(992898167,'PCS',0,0,0,176.69,-3.57,129.34,'LAB1O1, ER2, Test Cell'),(1026248823,'121f08',-90,90,0,118.14,53.32,160.52,'LAB1S3, MSG, Ceiling Plate A2-A3'),(1026249154,'SUBSA',0,0,0,106.65,56.48,181.12,'LAB1S3, MSG, SUBSA Thermal Chamber'),(1026249160,'ossbtmf',90,0,0,135.28,-10.68,132.12,'LAB1O2, ER1, Lockers 3,4'),(1026249161,'ossraw',90,0,0,135.28,-10.68,132.12,'LAB1O2, ER1, Lockers 3,4'),(1030032851,'121f08',-90,90,0,115.21,53.41,160.98,'LAB1S3, MSG, Ceiling Plate A2-A3'),(1026249162,'ossfbias',90,0,0,135.28,-10.68,132.12,'LAB1O2, ER1, Lockers 3,4'),(1041853800,'121f02',-90,0,-90,128.73,-23.53,144.15,'LAB1O2, ER1, Drawer 1'),(1041841800,'121f02',0,0,-90,118.45,-38.36,170.57,'LAB1P3, CEVIS, Frame'),(1042731541,'radgse',0,0,0,0,0,0,'ISS radgse PAD archive support'),(1058459102,'121f08',90,90,0,87.99,55.19,160.98,'LAB1S3, MSG, Ceiling Plate D3-D2'),(1061856000,'121f08',-90,90,0,118.14,53.32,160.52,'LAB1S3, MSG, Ceiling Plate A2-A3'),(1205193600,'0BBD',0,90,0,387.48,-212.75,156.34,'JPM_A3_Upper-left'),(1218724727,'COL1F2',0,0,0,489.96,147.96,190.92,'COL1F2, MSG, Center of Rack'),(1197460800,'121f08',90,90,0,87.99,55.19,160.98,'LAB1S3, MSG, Ceiling Plate D3-D2'),(1205193600,'0BBC',180,0,0,383.38,-236.87,191.98,'JPM_A3_SCOF_REF-CELL'),(1205193600,'0BBB',0,90,0,387.48,-170.75,156.34,'JPM_A2_Upper-left'),(1235952000,'es05',180,0,90,116.81,40.39,192.76,'LAB1S3, CIR, Front Panel'),(1240790400,'121f08',0,180,0,374.17,166.19,157.03,'COL1A1, ER3, B2 Panel'),(1242604800,'121f05',-90,-90,0,466.8,-292.06,214.58,'JPM1F5, ER4, Drawer 2'),(1253750400,'es08',0,90,-90,475.71,235.22,160.27,'COL1F2, MSG, Ceiling Plate Y1-C3 Y2-D3'),(1256515200,'121F02',90,-45,-90,395.08,287.99,232.22,'COL1D3, Forward Foot of FWED'),(1254096000,'es06',0,180,0,69.31,40.39,196.41,'LAB1S4, FIR, '),(1272672000,'es08',0,90,90,475.63,204.91,159.95,'COL1F2, MSG, Ceiling Plage Y1-B1 Y2-A1'),(1289433600,'121f08',0,90,0,434.37,183.25,147.01,'COL1O1, FSL, ODM Seat Track'),(1275350400,'es08',0,90,-90,475.71,235.22,160.27,'COL1F2, MSG, Ceiling Plage Y1-C3 Y2-D3'),(1294617600,'121f08',0,-90,0,378.11,246.46,234.96,'COL1D3,  Seat Track near A3'),(1294940070,'MSG Rack',0,180,0,143.7,57.01,190.05,'LAB1S2, Center of Rack  '),(1297879200,'121f08',0,90,0,434.37,183.25,147.01,'COL1O1, FSL, ODM Seat Track'),(1301875200,'121f02',0,0,90,161.95,40.39,157.64,'LAB1S2, MSG, Upper Left Seat Track '),(1304380800,'MWA',0,0,0,143.7,-56.99,190.95,'LAB1P2,  Center of Rack'),(1304208000,'MSG Rack2',0,180,0,143.7,57.01,190.05,'LAB1S2, Center of Rack  '),(1315850400,'121f08',0,0,180,371.17,193.43,165.75,'COL1A1, ER3, Seat Track  near D1'),(1205193600,'0BBA',0,0,0,0,0,0,'JPM_F3_on_GHF-MP'),(1331054213,'MWA',0,0,0,185.7,57.01,190.05,'LAB1S1, Center of Rack  '),(1354647600,'121f08',0,90,0,434.37,183.25,147.01,'COL1O1, FSL, ODM Seat Track'),(1355231700,'121f08',0,0,180,371.17,193.43,165.75,'COL1A1, ER3, Seat Track  near D1'),(946684800,'es05',180,0,90,116.81,40.39,192.76,'LAB1S3, CIR, Front Panel'),(946684800,'es06',0,180,0,69.31,40.39,196.41,'LAB1S4, FIR, '),(1375387563,'es03',0,90,90,475.63,204.91,159.95,'LAB1S2, MSG, Ceiling Plate Y1-B1 Y2-A1'),(1375974000,'121f02',0,-90,0,378.11,246.46,234.96,'COL1D3,  Seat Track near A3');
/*!40000 ALTER TABLE `coord_system_db` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_coord_system`
--

DROP TABLE IF EXISTS `data_coord_system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_coord_system` (
  `time` double NOT NULL DEFAULT '0',
  `sensor` varchar(20) NOT NULL DEFAULT '',
  `coord_name` text,
  PRIMARY KEY (`time`,`sensor`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_coord_system`
--

LOCK TABLES `data_coord_system` WRITE;
/*!40000 ALTER TABLE `data_coord_system` DISABLE KEYS */;
INSERT INTO `data_coord_system` VALUES (988749145,'hirap','hirap'),(1026324505,'ossfbias','oss'),(975681310,'121f06','121f06'),(975681311,'121f02','121f02'),(975681313,'121f03','121f03'),(975681314,'121f04','121f04'),(975681315,'121f05','121f05'),(1023969600,'121f04','SSAnalysis'),(1023969600,'121f05','SSAnalysis'),(1023969600,'121f03','SSAnalysis'),(1023969600,'121f02','SSAnalysis'),(1023969600,'hirap','SSAnalysis'),(988749145,'oss','oss'),(1023969600,'oss','SSAnalysis'),(1026324506,'ossraw','ossraw'),(1026324503,'121f08','SSAnalysis'),(1042731540,'oare','oare'),(1026324504,'ossbtmf','SSAnalysis'),(1042731541,'radgse','radgse'),(1243866611,'es05','SSAnalysis'),(1078236000,'es13','es13'),(1217548800,'0BBB','SSAnalysis'),(1217548800,'0BBC','0BBC'),(1217548800,'0BBD','SSAnalysis'),(1236211200,'es05','es05'),(1253750400,'es08','SSAnalysis'),(1254096000,'es06','SSAnalysis'),(1254009600,'121f02','121f02'),(1205193600,'0BBA','0BBA'),(1375387563,'es03','SSAnalysis'),(1375974000,'121f02','SSAnalysis');
/*!40000 ALTER TABLE `data_coord_system` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'pad'
--

--
-- Dumping routines for database 'pad'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-12-12 14:01:22
