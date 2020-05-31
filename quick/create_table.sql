use iosclub;
CREATE TABLE `memberlist` (
  `member_id` int unsigned UNIQUE NOT NULL AUTO_INCREMENT,
  `member_name` varchar(50) CHARACTER SET utf8mb4 NOT NULL DEFAULT 'None',
  `member_nid` varchar(50) NOT NULL DEFAULT 'None',
  `member_department` varchar(100) CHARACTER SET utf8mb4 NOT NULL DEFAULT 'None',
  `join_date` date NOT NULL DEFAULT '1001-01-01',
  `admission_year` int unsigned NOT NULL DEFAULT 0,
  `sex` varchar(1) not null DEFAULT 'N',
  `e-mail` varchar(100) not null DEFAULT 'None',
  `birth` date not null DEFAULT '1001-01-01',
  PRIMARY KEY (`member_id`)
);

create table `class_state`(
	`class_state_id` int unsigned UNIQUE not null auto_increment,
	`member_id` int unsigned NOT NULL,
    `date` timestamp not null,
    `attendance` bool not null,
    `register` bool not null,
    FOREIGN KEY(`member_id`) references memberlist(`member_id`),
    primary key(`class_state_id`)
);

create table `rtc_state`(
	`rtc_state_id` int unsigned UNIQUE not null auto_increment,
    `date` timestamp not null,
    `member_id` int unsigned NOT NULL,
    `access` bool not null,
    `serial_number` bigint not null,
    foreign key(`member_id`) references memberlist(`member_id`),
    primary key(`rtc_state_id`)
);