/*
Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
Copyright (C) 2016 - 2021 viral32111 (https://viral32111.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see http://www.gnu.org/licenses/.
*/

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ConspiracyAI` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ConspiracyAI`;
DROP TABLE IF EXISTS `AnonMessages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AnonMessages` (
  `Message` varchar(24) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL COMMENT 'Identifier of the message',
  `Token` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL COMMENT 'Token to delete the message',
  PRIMARY KEY (`Message`),
  UNIQUE KEY `Token` (`Token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Deletion tokens for anonymous messages';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `MemberStatistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MemberStatistics` (
  `Member` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL COMMENT 'Identifier of the member',
  `Messages` int NOT NULL DEFAULT '1' COMMENT 'Number of messages sent',
  `Edits` int NOT NULL DEFAULT '0' COMMENT 'Number of messages edited',
  `Deletions` int NOT NULL DEFAULT '0' COMMENT 'Number of messages deleted',
  PRIMARY KEY (`Member`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Statistics for each member';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Members` (
  `Member` binary(32) NOT NULL,
  `Steam` binary(32) DEFAULT NULL,
  `Joined` binary(16) NOT NULL,
  PRIMARY KEY (`Member`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Members who have joined the Discord server';
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `RepostHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RepostHistory` (
  `Checksum` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL COMMENT 'Hash of the content',
  `Channel` bigint NOT NULL COMMENT 'The channel',
  `Message` bigint NOT NULL COMMENT 'The message',
  `Count` int NOT NULL DEFAULT '1' COMMENT 'Times the content has been seen',
  PRIMARY KEY (`Checksum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Images, videos and audio for repost checking';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
