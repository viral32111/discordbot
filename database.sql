/*
Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
Copyright (C) 2016 - 2020 viral32111 (https://viral32111.com)

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

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `AnonMessages` (
	`Message` varchar(24) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
	`Token` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Members` (
	`Member` binary(32) NOT NULL,
	`Steam` binary(32) DEFAULT NULL,
	`Joined` binary(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `MemberStatistics` (
	`Member` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
	`Messages` int NOT NULL DEFAULT '1',
	`Edits` int NOT NULL DEFAULT '0',
	`Deletions` int NOT NULL DEFAULT '0',
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `RelayShortlinks` (
	`Checksum` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
	`Link` varchar(8) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `RepostHistory` (
	`Checksum` varchar(64) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
	`Channel` bigint NOT NULL,
	`Message` bigint NOT NULL,
`Count` int NOT NULL DEFAULT '1',
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


ALTER TABLE `AnonMessages`
	ADD PRIMARY KEY (`Message`),
	ADD UNIQUE KEY `Token` (`Token`);

ALTER TABLE `Members`
	ADD PRIMARY KEY (`Member`);

ALTER TABLE `MemberStatistics`
	ADD PRIMARY KEY (`Member`);

ALTER TABLE `RelayShortlinks`
	ADD PRIMARY KEY (`Checksum`),
	ADD UNIQUE KEY `LINK` (`Link`) USING BTREE;

ALTER TABLE `RepostHistory`
	ADD PRIMARY KEY (`Checksum`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
