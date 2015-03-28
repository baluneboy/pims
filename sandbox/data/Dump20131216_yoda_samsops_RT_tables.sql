CREATE DATABASE  IF NOT EXISTS `samsops` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `samsops`;
-- MySQL dump 10.13  Distrib 5.5.29, for debian-linux-gnu (x86_64)
--
-- Host: yoda    Database: samsops
-- ------------------------------------------------------
-- Server version	5.1.41

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
-- Table structure for table `RT_EE_gse_data`
--

DROP TABLE IF EXISTS `RT_EE_gse_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RT_EE_gse_data` (
  `EE_id` char(20) DEFAULT NULL,
  `er_dwr_current` double DEFAULT NULL,
  `er_drw_comm` int(11) DEFAULT NULL,
  `ecw_word` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RT_EE_gse_data`
--

LOCK TABLES `RT_EE_gse_data` WRITE;
/*!40000 ALTER TABLE `RT_EE_gse_data` DISABLE KEYS */;
INSERT INTO `RT_EE_gse_data` VALUES ('122-f02',0.515625,1,0),('122-f03',0.732422,1,0),('122-f04',0,99,99),('122-f05',0,99,99),('122-f06',1,99,99),('122-f01',0,99,99),('122-f07',0,99,99);
/*!40000 ALTER TABLE `RT_EE_gse_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RT_TSHES_House_data`
--

DROP TABLE IF EXISTS `RT_TSHES_House_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RT_TSHES_House_data` (
  `tshes_id` char(20) DEFAULT NULL,
  `tshes_timestamp` datetime DEFAULT NULL,
  `xtemp` double DEFAULT NULL,
  `ytemp` double DEFAULT NULL,
  `ztemp` double DEFAULT NULL,
  `p5V` double DEFAULT NULL,
  `p15V` double DEFAULT NULL,
  `dig_io_stat` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RT_TSHES_House_data`
--

LOCK TABLES `RT_TSHES_House_data` WRITE;
/*!40000 ALTER TABLE `RT_TSHES_House_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `RT_TSHES_House_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RT_EE_telem_data`
--

DROP TABLE IF EXISTS `RT_EE_telem_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RT_EE_telem_data` (
  `EE_id` char(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `baseplate_temp` double DEFAULT NULL,
  `plus5_volt` double DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RT_EE_telem_data`
--

LOCK TABLES `RT_EE_telem_data` WRITE;
/*!40000 ALTER TABLE `RT_EE_telem_data` DISABLE KEYS */;
INSERT INTO `RT_EE_telem_data` VALUES ('122-f02','2013-12-16 15:40:32',24.7827,5.12534),('122-f03','2013-12-11 15:56:34',24.8082,5.11731),('122-f04','2013-12-11 15:21:58',20.8964,5.13204),('122-f05','2013-08-08 13:03:52',21.2364,5.17719),('122-f06',NULL,NULL,NULL),('122-f01','2012-08-24 15:08:22',-270.299,-0.00109803),('122-f07','2011-11-04 15:31:53',23.8427,5.13071);
/*!40000 ALTER TABLE `RT_EE_telem_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RT_ICU_gse_data`
--

DROP TABLE IF EXISTS `RT_ICU_gse_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RT_ICU_gse_data` (
  `ICU_name` char(20) DEFAULT NULL,
  `ICU_er_drw_current` double DEFAULT NULL,
  `ICU_er_drw_comm` int(11) DEFAULT NULL,
  `ICU_ecw_word` int(11) DEFAULT NULL,
  `GSE_tiss_time` char(50) DEFAULT NULL,
  `GSE_aos_los` int(11) DEFAULT NULL,
  `GSE_aos_los_status` char(20) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RT_ICU_gse_data`
--

LOCK TABLES `RT_ICU_gse_data` WRITE;
/*!40000 ALTER TABLE `RT_ICU_gse_data` DISABLE KEYS */;
INSERT INTO `RT_ICU_gse_data` VALUES ('icu-f01',1.11254e-308,0,0,'Mon Dec 16 15:40:33 2013',1,' / /');
/*!40000 ALTER TABLE `RT_ICU_gse_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RT_ICU_telem_data`
--

DROP TABLE IF EXISTS `RT_ICU_telem_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RT_ICU_telem_data` (
  `ICU_name` char(20) DEFAULT NULL,
  `ICU_timestamp` datetime DEFAULT NULL,
  `ICU_out_air_temp` double DEFAULT NULL,
  `ICU_battery_charge` double DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RT_ICU_telem_data`
--

LOCK TABLES `RT_ICU_telem_data` WRITE;
/*!40000 ALTER TABLE `RT_ICU_telem_data` DISABLE KEYS */;
INSERT INTO `RT_ICU_telem_data` VALUES ('icu-f01','2013-12-16 15:40:34',25.1358,0);
/*!40000 ALTER TABLE `RT_ICU_telem_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'samsops'
--

--
-- Dumping routines for database 'samsops'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-12-16 15:37:55
