PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Product" (
	id INTEGER NOT NULL, 
	name VARCHAR(45) NOT NULL, 
	price INTEGER NOT NULL, 
	category_id INTEGER, 
	available BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES "Category" (id), 
	CHECK (available IN (0, 1))
);
INSERT INTO Product VALUES(1,'綜合生魚片',240,1,1);
INSERT INTO Product VALUES(2,'滷肉飯',30,2,1);
INSERT INTO Product VALUES(3,'麻油川七',160,5,1);
INSERT INTO Product VALUES(4,'炒海瓜子',180,4,1);
INSERT INTO Product VALUES(5,'皮蛋地瓜葉',160,5,1);
INSERT INTO Product VALUES(6,'麻油藥膳正土羊肉鍋（配套）',800,6,1);
INSERT INTO Product VALUES(7,'鮭魚生魚片',240,1,1);
INSERT INTO Product VALUES(8,'軟時生魚片',280,1,1);
INSERT INTO Product VALUES(9,'旗魚生魚片',200,1,1);
INSERT INTO Product VALUES(10,'泥信生魚片',200,1,1);
INSERT INTO Product VALUES(11,'燻雞（半隻）',280,1,1);
INSERT INTO Product VALUES(12,'油雞',360,1,1);
INSERT INTO Product VALUES(13,'蒜蓉小卷',160,1,1);
INSERT INTO Product VALUES(14,'冰島鱈魚肝',180,1,1);
INSERT INTO Product VALUES(15,'香魚甘露煮（一尾）',80,1,1);
INSERT INTO Product VALUES(16,'蟹肉沙拉',180,1,1);
INSERT INTO Product VALUES(17,'智利鮑角沙拉',260,1,1);
INSERT INTO Product VALUES(18,'涼拌雪花翅',200,1,1);
INSERT INTO Product VALUES(19,'蜜汁黑豆',120,1,1);
INSERT INTO Product VALUES(20,'北歐沙拉',200,1,1);
INSERT INTO Product VALUES(21,'冷筍沙拉',200,1,1);
INSERT INTO Product VALUES(22,'油飯',100,2,1);
INSERT INTO Product VALUES(23,'炒飯',80,2,1);
INSERT INTO Product VALUES(24,'炒麵',80,2,1);
INSERT INTO Product VALUES(25,'魚皮白菜滷',180,2,1);
INSERT INTO Product VALUES(26,'炒米粉',80,2,1);
INSERT INTO Product VALUES(27,'滷筍絲',80,2,1);
INSERT INTO Product VALUES(28,'臭豆腐（6塊）',200,2,1);
INSERT INTO Product VALUES(29,'筍絲滷肉',240,2,1);
INSERT INTO Product VALUES(30,'筍絲腿包',320,2,1);
INSERT INTO Product VALUES(31,'筍絲豬腳（10塊）',320,2,1);
INSERT INTO Product VALUES(32,'炒蚋仔',160,4,1);
INSERT INTO Product VALUES(33,'沙茶螺肉',160,4,1);
INSERT INTO Product VALUES(34,'炒雪螺',160,4,1);
INSERT INTO Product VALUES(35,'客家小炒',160,4,1);
INSERT INTO Product VALUES(36,'黑胡椒鳳螺',480,4,1);
INSERT INTO Product VALUES(37,'燙蝦',320,4,1);
INSERT INTO Product VALUES(38,'蒜泥草蝦（4尾）',320,4,1);
INSERT INTO Product VALUES(39,'滑蛋蝦仁',280,4,1);
INSERT INTO Product VALUES(40,'蒜泥蚵',220,4,1);
INSERT INTO Product VALUES(41,'蔭司蚵',220,4,1);
INSERT INTO Product VALUES(42,'宮保臭豆腐',160,4,1);
INSERT INTO Product VALUES(43,'宮保皮蛋',160,4,1);
INSERT INTO Product VALUES(44,'宮保雞丁',240,4,1);
INSERT INTO Product VALUES(45,'炒中卷',240,4,1);
INSERT INTO Product VALUES(46,'金沙中卷',240,4,1);
INSERT INTO Product VALUES(47,'五味中卷',260,4,1);
INSERT INTO Product VALUES(48,'五味軟時',360,4,1);
INSERT INTO Product VALUES(49,'炒蟹腳',280,4,1);
INSERT INTO Product VALUES(50,'九層塔蛋',100,4,1);
INSERT INTO Product VALUES(51,'菜脯蛋',100,4,1);
INSERT INTO Product VALUES(52,'蔥蛋',100,4,1);
INSERT INTO Product VALUES(53,'海鮮咖哩堡（5片）',360,4,1);
INSERT INTO Product VALUES(54,'港式鳳爪',120,4,1);
INSERT INTO Product VALUES(55,'麻婆豆腐',160,4,1);
INSERT INTO Product VALUES(56,'五更腸旺',180,4,1);
INSERT INTO Product VALUES(57,'炒鵝腸',200,4,1);
INSERT INTO Product VALUES(58,'炒大腸',200,4,1);
INSERT INTO Product VALUES(59,'黑椒朱肩排（支）',100,4,1);
INSERT INTO Product VALUES(60,'醬汁瓜子肉',220,4,1);
INSERT INTO Product VALUES(61,'蒜苗鹹豬肉',200,4,1);
INSERT INTO Product VALUES(62,'麻油松阪豬',360,4,1);
INSERT INTO Product VALUES(63,'麻油腰只',360,4,1);
INSERT INTO Product VALUES(64,'麻油雙腰',560,4,1);
INSERT INTO Product VALUES(65,'紅燒牛腩煲',320,4,1);
INSERT INTO Product VALUES(66,'三杯中卷',450,7,1);
INSERT INTO Product VALUES(67,'炒牛肉',160,4,1);
INSERT INTO Product VALUES(68,'三杯田雞',450,7,1);
INSERT INTO Product VALUES(69,'鐵板鹿肉',260,9,1);
INSERT INTO Product VALUES(70,'鐵板牛肉',320,9,1);
INSERT INTO Product VALUES(71,'三杯土雞',450,7,1);
INSERT INTO Product VALUES(72,'炒羊肉',160,4,1);
INSERT INTO Product VALUES(73,'鐵板鴕鳥',260,9,1);
INSERT INTO Product VALUES(74,'鐵板豆腐',220,9,1);
INSERT INTO Product VALUES(75,'清炒地瓜葉',100,5,1);
INSERT INTO Product VALUES(76,'五味鳳螺',240,4,1);
INSERT INTO Product VALUES(77,'鐵板鮮蚵',260,9,1);
INSERT INTO Product VALUES(78,'烤秋刀魚（2隻）',140,10,1);
INSERT INTO Product VALUES(79,'炒劍荀',160,4,1);
INSERT INTO Product VALUES(80,'鹽烤鯖魚',200,10,1);
INSERT INTO Product VALUES(81,'炸花枝丸（6粒）',120,4,1);
INSERT INTO Product VALUES(82,'炸紅㷮鳗',240,4,1);
INSERT INTO Product VALUES(83,'炸水晶魚',160,4,1);
INSERT INTO Product VALUES(84,'烤鮭魚頭（半個）',250,10,1);
INSERT INTO Product VALUES(85,'炸西施捲（5條）',180,4,1);
INSERT INTO Product VALUES(86,'烤鹹豬肉',200,10,1);
INSERT INTO Product VALUES(87,'蚵仔酥',160,4,1);
INSERT INTO Product VALUES(88,'烤牛小排',260,10,1);
INSERT INTO Product VALUES(89,'炒水蓮',160,5,1);
INSERT INTO Product VALUES(90,'脆皮肥腸',200,4,1);
INSERT INTO Product VALUES(91,'鹹酥龍珠',160,4,1);
INSERT INTO Product VALUES(92,'鳳梨蝦球',240,4,1);
INSERT INTO Product VALUES(93,'塔香茄子',160,5,1);
INSERT INTO Product VALUES(94,'鹹酥蝦',320,4,1);
INSERT INTO Product VALUES(95,'金沙南瓜',120,5,1);
INSERT INTO Product VALUES(96,'月亮蝦餅',160,4,1);
INSERT INTO Product VALUES(97,'苦瓜鹹蛋',160,5,1);
INSERT INTO Product VALUES(98,'陶板絲瓜',360,5,1);
INSERT INTO Product VALUES(99,'炒空心菜',100,5,1);
INSERT INTO Product VALUES(100,'炒高麗菜',100,5,1);
INSERT INTO Product VALUES(101,'砂鍋魚頭',580,6,1);
INSERT INTO Product VALUES(102,'炒絲瓜',100,5,1);
INSERT INTO Product VALUES(103,'苦瓜雞鍋',580,6,1);
INSERT INTO Product VALUES(104,'炒山蘇',200,5,1);
INSERT INTO Product VALUES(105,'蛤蜊絲瓜',200,5,1);
INSERT INTO Product VALUES(106,'鮭魚頭味噌鍋',250,6,1);
INSERT INTO Product VALUES(107,'虎班',999,8,1);
INSERT INTO Product VALUES(108,'石班',499,8,1);
INSERT INTO Product VALUES(109,'鹹菜鴨肚鍋',360,6,1);
INSERT INTO Product VALUES(110,'蟲草雞鍋',580,6,1);
INSERT INTO Product VALUES(111,'鮮魚味噌湯',120,6,1);
INSERT INTO Product VALUES(112,'薑絲蛤蜊湯',180,6,1);
INSERT INTO Product VALUES(113,'黃魚（清蒸糖醋煎）',399,8,1);
INSERT INTO Product VALUES(114,'鹹菜蚵仔湯',160,6,1);
INSERT INTO Product VALUES(115,'鱈魚（清蒸豆酥）',360,8,1);
INSERT INTO Product VALUES(116,'哈根達斯冰淇淋（杯）',60,6,1);
INSERT INTO Product VALUES(117,'鹽酥雞軟骨',280,4,1);
INSERT INTO Product VALUES(118,'府城蝦捲（5條）',180,4,1);
INSERT INTO Product VALUES(119,'鹹酥軟殻蟹（2隻）',300,4,1);
INSERT INTO Product VALUES(120,'芝麻球6粒',150,4,1);
INSERT INTO Product VALUES(121,'果汁',60,11,1);
INSERT INTO Product VALUES(122,'金啤',65,11,1);
INSERT INTO Product VALUES(123,'台啤',60,11,1);
INSERT INTO Product VALUES(124,'18天',90,11,1);
INSERT INTO Product VALUES(125,'虎牌',60,11,1);
INSERT INTO Product VALUES(126,'海尼根',100,11,1);
INSERT INTO Product VALUES(127,'青島生啤（杯）',60,11,1);
INSERT INTO Product VALUES(128,'半天水',60,11,1);
INSERT INTO Product VALUES(129,'西打',60,11,1);
INSERT INTO Product VALUES(130,'蘆薈',60,11,1);
INSERT INTO Product VALUES(131,'蕃茄汁',40,11,1);
INSERT INTO Product VALUES(132,'礦泉水',40,11,1);
INSERT INTO Product VALUES(133,'台灣生啤（杯）',60,11,1);
INSERT INTO Product VALUES(134,'烤牛肉串（份）',200,10,1);
INSERT INTO Product VALUES(135,'烤羊肉串（份）',180,10,1);
INSERT INTO Product VALUES(136,'烤豬肉串（份）',160,10,1);
INSERT INTO Product VALUES(137,'烤雞肉串（份）',160,10,1);
INSERT INTO Product VALUES(138,'長尾鳥生片、湯',1500,1,1);
INSERT INTO Product VALUES(139,'烤味噌魚',200,10,1);
INSERT INTO Product VALUES(140,'烤活吳郭魚',360,10,1);
INSERT INTO Product VALUES(141,'烤小伍魚每尾',120,10,1);
INSERT INTO Product VALUES(142,'鹹酥萬里香',240,4,1);
INSERT INTO Product VALUES(143,'大壺生啤酒',420,11,1);
INSERT INTO Product VALUES(144,'紹興酒',200,11,1);
INSERT INTO Product VALUES(145,'紅露酒',200,11,1);
INSERT INTO Product VALUES(146,'黃酒',200,11,1);
INSERT INTO Product VALUES(147,'紅麴葡萄酒',450,11,1);
INSERT INTO Product VALUES(148,'玉泉清酒',200,11,1);
INSERT INTO Product VALUES(149,'柯提葡萄酒',499,11,1);
INSERT INTO Product VALUES(150,'毆肯達紅酒',499,11,1);
INSERT INTO Product VALUES(151,'蘇格蘭12年',1400,11,1);
INSERT INTO Product VALUES(152,'約翰走路15年',1500,11,1);
INSERT INTO Product VALUES(153,'約翰走路12年',1100,11,1);
INSERT INTO Product VALUES(154,'仕高利達',700,11,1);
INSERT INTO Product VALUES(155,'大38高梁酒',800,11,1);
INSERT INTO Product VALUES(156,'大58高梁酒',900,11,1);
INSERT INTO Product VALUES(157,'小58高梁酒',350,11,1);
INSERT INTO Product VALUES(158,'小38高梁酒',350,11,1);
INSERT INTO Product VALUES(159,'合菜$3000',3000,3,1);
INSERT INTO Product VALUES(160,'合菜$3500',3500,3,1);
INSERT INTO Product VALUES(161,'合菜$4000',4000,3,1);
INSERT INTO Product VALUES(162,'合菜$5000',5000,3,1);
COMMIT;
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "PosProduct" (
	pos_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (pos_id, product_id), 
	FOREIGN KEY(pos_id) REFERENCES "POS" (id), 
	FOREIGN KEY(product_id) REFERENCES "Product" (id)
);
INSERT INTO PosProduct VALUES(1,1);
INSERT INTO PosProduct VALUES(3,1);
INSERT INTO PosProduct VALUES(1,2);
INSERT INTO PosProduct VALUES(3,2);
INSERT INTO PosProduct VALUES(1,3);
INSERT INTO PosProduct VALUES(3,3);
INSERT INTO PosProduct VALUES(1,4);
INSERT INTO PosProduct VALUES(3,4);
INSERT INTO PosProduct VALUES(1,5);
INSERT INTO PosProduct VALUES(3,5);
INSERT INTO PosProduct VALUES(1,6);
INSERT INTO PosProduct VALUES(3,6);
INSERT INTO PosProduct VALUES(1,7);
INSERT INTO PosProduct VALUES(3,7);
INSERT INTO PosProduct VALUES(1,8);
INSERT INTO PosProduct VALUES(3,8);
INSERT INTO PosProduct VALUES(1,9);
INSERT INTO PosProduct VALUES(3,9);
INSERT INTO PosProduct VALUES(1,10);
INSERT INTO PosProduct VALUES(3,10);
INSERT INTO PosProduct VALUES(1,11);
INSERT INTO PosProduct VALUES(3,11);
INSERT INTO PosProduct VALUES(1,12);
INSERT INTO PosProduct VALUES(3,12);
INSERT INTO PosProduct VALUES(1,13);
INSERT INTO PosProduct VALUES(3,13);
INSERT INTO PosProduct VALUES(1,14);
INSERT INTO PosProduct VALUES(3,14);
INSERT INTO PosProduct VALUES(1,15);
INSERT INTO PosProduct VALUES(3,15);
INSERT INTO PosProduct VALUES(1,16);
INSERT INTO PosProduct VALUES(3,16);
INSERT INTO PosProduct VALUES(1,17);
INSERT INTO PosProduct VALUES(3,17);
INSERT INTO PosProduct VALUES(1,18);
INSERT INTO PosProduct VALUES(3,18);
INSERT INTO PosProduct VALUES(1,19);
INSERT INTO PosProduct VALUES(3,19);
INSERT INTO PosProduct VALUES(1,20);
INSERT INTO PosProduct VALUES(3,20);
INSERT INTO PosProduct VALUES(1,21);
INSERT INTO PosProduct VALUES(3,21);
INSERT INTO PosProduct VALUES(1,22);
INSERT INTO PosProduct VALUES(3,22);
INSERT INTO PosProduct VALUES(1,23);
INSERT INTO PosProduct VALUES(3,23);
INSERT INTO PosProduct VALUES(1,24);
INSERT INTO PosProduct VALUES(3,24);
INSERT INTO PosProduct VALUES(1,25);
INSERT INTO PosProduct VALUES(3,25);
INSERT INTO PosProduct VALUES(1,26);
INSERT INTO PosProduct VALUES(3,26);
INSERT INTO PosProduct VALUES(1,27);
INSERT INTO PosProduct VALUES(3,27);
INSERT INTO PosProduct VALUES(1,28);
INSERT INTO PosProduct VALUES(3,28);
INSERT INTO PosProduct VALUES(1,29);
INSERT INTO PosProduct VALUES(3,29);
INSERT INTO PosProduct VALUES(1,30);
INSERT INTO PosProduct VALUES(3,30);
INSERT INTO PosProduct VALUES(1,31);
INSERT INTO PosProduct VALUES(3,31);
INSERT INTO PosProduct VALUES(1,32);
INSERT INTO PosProduct VALUES(3,32);
INSERT INTO PosProduct VALUES(1,33);
INSERT INTO PosProduct VALUES(3,33);
INSERT INTO PosProduct VALUES(1,34);
INSERT INTO PosProduct VALUES(3,34);
INSERT INTO PosProduct VALUES(1,35);
INSERT INTO PosProduct VALUES(3,35);
INSERT INTO PosProduct VALUES(1,36);
INSERT INTO PosProduct VALUES(3,36);
INSERT INTO PosProduct VALUES(1,37);
INSERT INTO PosProduct VALUES(3,37);
INSERT INTO PosProduct VALUES(1,38);
INSERT INTO PosProduct VALUES(3,38);
INSERT INTO PosProduct VALUES(1,39);
INSERT INTO PosProduct VALUES(3,39);
INSERT INTO PosProduct VALUES(1,40);
INSERT INTO PosProduct VALUES(3,40);
INSERT INTO PosProduct VALUES(1,41);
INSERT INTO PosProduct VALUES(3,41);
INSERT INTO PosProduct VALUES(1,42);
INSERT INTO PosProduct VALUES(3,42);
INSERT INTO PosProduct VALUES(1,43);
INSERT INTO PosProduct VALUES(3,43);
INSERT INTO PosProduct VALUES(1,44);
INSERT INTO PosProduct VALUES(3,44);
INSERT INTO PosProduct VALUES(1,45);
INSERT INTO PosProduct VALUES(3,45);
INSERT INTO PosProduct VALUES(1,46);
INSERT INTO PosProduct VALUES(3,46);
INSERT INTO PosProduct VALUES(1,47);
INSERT INTO PosProduct VALUES(3,47);
INSERT INTO PosProduct VALUES(1,48);
INSERT INTO PosProduct VALUES(3,48);
INSERT INTO PosProduct VALUES(1,49);
INSERT INTO PosProduct VALUES(3,49);
INSERT INTO PosProduct VALUES(1,50);
INSERT INTO PosProduct VALUES(3,50);
INSERT INTO PosProduct VALUES(1,51);
INSERT INTO PosProduct VALUES(3,51);
INSERT INTO PosProduct VALUES(1,52);
INSERT INTO PosProduct VALUES(3,52);
INSERT INTO PosProduct VALUES(1,53);
INSERT INTO PosProduct VALUES(3,53);
INSERT INTO PosProduct VALUES(1,54);
INSERT INTO PosProduct VALUES(3,54);
INSERT INTO PosProduct VALUES(1,55);
INSERT INTO PosProduct VALUES(3,55);
INSERT INTO PosProduct VALUES(1,56);
INSERT INTO PosProduct VALUES(3,56);
INSERT INTO PosProduct VALUES(1,57);
INSERT INTO PosProduct VALUES(3,57);
INSERT INTO PosProduct VALUES(1,58);
INSERT INTO PosProduct VALUES(3,58);
INSERT INTO PosProduct VALUES(1,59);
INSERT INTO PosProduct VALUES(3,59);
INSERT INTO PosProduct VALUES(1,60);
INSERT INTO PosProduct VALUES(3,60);
INSERT INTO PosProduct VALUES(1,61);
INSERT INTO PosProduct VALUES(3,61);
INSERT INTO PosProduct VALUES(1,62);
INSERT INTO PosProduct VALUES(3,62);
INSERT INTO PosProduct VALUES(1,63);
INSERT INTO PosProduct VALUES(3,63);
INSERT INTO PosProduct VALUES(1,64);
INSERT INTO PosProduct VALUES(3,64);
INSERT INTO PosProduct VALUES(1,65);
INSERT INTO PosProduct VALUES(3,65);
INSERT INTO PosProduct VALUES(1,67);
INSERT INTO PosProduct VALUES(3,67);
INSERT INTO PosProduct VALUES(1,69);
INSERT INTO PosProduct VALUES(3,69);
INSERT INTO PosProduct VALUES(1,70);
INSERT INTO PosProduct VALUES(3,70);
INSERT INTO PosProduct VALUES(1,72);
INSERT INTO PosProduct VALUES(3,72);
INSERT INTO PosProduct VALUES(1,73);
INSERT INTO PosProduct VALUES(3,73);
INSERT INTO PosProduct VALUES(1,74);
INSERT INTO PosProduct VALUES(3,74);
INSERT INTO PosProduct VALUES(1,76);
INSERT INTO PosProduct VALUES(3,76);
INSERT INTO PosProduct VALUES(1,77);
INSERT INTO PosProduct VALUES(3,77);
INSERT INTO PosProduct VALUES(1,75);
INSERT INTO PosProduct VALUES(3,75);
INSERT INTO PosProduct VALUES(1,79);
INSERT INTO PosProduct VALUES(3,79);
INSERT INTO PosProduct VALUES(1,66);
INSERT INTO PosProduct VALUES(3,66);
INSERT INTO PosProduct VALUES(1,68);
INSERT INTO PosProduct VALUES(3,68);
INSERT INTO PosProduct VALUES(1,71);
INSERT INTO PosProduct VALUES(3,71);
INSERT INTO PosProduct VALUES(1,80);
INSERT INTO PosProduct VALUES(3,80);
INSERT INTO PosProduct VALUES(1,81);
INSERT INTO PosProduct VALUES(3,81);
INSERT INTO PosProduct VALUES(1,78);
INSERT INTO PosProduct VALUES(3,78);
INSERT INTO PosProduct VALUES(1,82);
INSERT INTO PosProduct VALUES(3,82);
INSERT INTO PosProduct VALUES(1,83);
INSERT INTO PosProduct VALUES(3,83);
INSERT INTO PosProduct VALUES(1,84);
INSERT INTO PosProduct VALUES(3,84);
INSERT INTO PosProduct VALUES(1,85);
INSERT INTO PosProduct VALUES(3,85);
INSERT INTO PosProduct VALUES(1,86);
INSERT INTO PosProduct VALUES(3,86);
INSERT INTO PosProduct VALUES(1,87);
INSERT INTO PosProduct VALUES(3,87);
INSERT INTO PosProduct VALUES(1,88);
INSERT INTO PosProduct VALUES(3,88);
INSERT INTO PosProduct VALUES(1,89);
INSERT INTO PosProduct VALUES(3,89);
INSERT INTO PosProduct VALUES(1,90);
INSERT INTO PosProduct VALUES(3,90);
INSERT INTO PosProduct VALUES(1,91);
INSERT INTO PosProduct VALUES(3,91);
INSERT INTO PosProduct VALUES(1,92);
INSERT INTO PosProduct VALUES(3,92);
INSERT INTO PosProduct VALUES(1,93);
INSERT INTO PosProduct VALUES(3,93);
INSERT INTO PosProduct VALUES(1,94);
INSERT INTO PosProduct VALUES(3,94);
INSERT INTO PosProduct VALUES(1,95);
INSERT INTO PosProduct VALUES(3,95);
INSERT INTO PosProduct VALUES(1,96);
INSERT INTO PosProduct VALUES(3,96);
INSERT INTO PosProduct VALUES(1,97);
INSERT INTO PosProduct VALUES(3,97);
INSERT INTO PosProduct VALUES(1,98);
INSERT INTO PosProduct VALUES(3,98);
INSERT INTO PosProduct VALUES(1,99);
INSERT INTO PosProduct VALUES(3,99);
INSERT INTO PosProduct VALUES(1,100);
INSERT INTO PosProduct VALUES(3,100);
INSERT INTO PosProduct VALUES(1,101);
INSERT INTO PosProduct VALUES(3,101);
INSERT INTO PosProduct VALUES(1,102);
INSERT INTO PosProduct VALUES(3,102);
INSERT INTO PosProduct VALUES(1,103);
INSERT INTO PosProduct VALUES(3,103);
INSERT INTO PosProduct VALUES(1,104);
INSERT INTO PosProduct VALUES(3,104);
INSERT INTO PosProduct VALUES(1,105);
INSERT INTO PosProduct VALUES(3,105);
INSERT INTO PosProduct VALUES(1,106);
INSERT INTO PosProduct VALUES(3,106);
INSERT INTO PosProduct VALUES(1,107);
INSERT INTO PosProduct VALUES(3,107);
INSERT INTO PosProduct VALUES(1,108);
INSERT INTO PosProduct VALUES(3,108);
INSERT INTO PosProduct VALUES(1,109);
INSERT INTO PosProduct VALUES(3,109);
INSERT INTO PosProduct VALUES(1,110);
INSERT INTO PosProduct VALUES(3,110);
INSERT INTO PosProduct VALUES(1,111);
INSERT INTO PosProduct VALUES(3,111);
INSERT INTO PosProduct VALUES(1,112);
INSERT INTO PosProduct VALUES(3,112);
INSERT INTO PosProduct VALUES(1,113);
INSERT INTO PosProduct VALUES(3,113);
INSERT INTO PosProduct VALUES(1,114);
INSERT INTO PosProduct VALUES(3,114);
INSERT INTO PosProduct VALUES(1,115);
INSERT INTO PosProduct VALUES(3,115);
INSERT INTO PosProduct VALUES(1,116);
INSERT INTO PosProduct VALUES(3,116);
INSERT INTO PosProduct VALUES(1,117);
INSERT INTO PosProduct VALUES(3,117);
INSERT INTO PosProduct VALUES(1,118);
INSERT INTO PosProduct VALUES(3,118);
INSERT INTO PosProduct VALUES(1,119);
INSERT INTO PosProduct VALUES(3,119);
INSERT INTO PosProduct VALUES(1,120);
INSERT INTO PosProduct VALUES(3,120);
INSERT INTO PosProduct VALUES(1,121);
INSERT INTO PosProduct VALUES(1,122);
INSERT INTO PosProduct VALUES(1,123);
INSERT INTO PosProduct VALUES(1,124);
INSERT INTO PosProduct VALUES(1,125);
INSERT INTO PosProduct VALUES(1,126);
INSERT INTO PosProduct VALUES(1,127);
INSERT INTO PosProduct VALUES(1,128);
INSERT INTO PosProduct VALUES(1,129);
INSERT INTO PosProduct VALUES(1,130);
INSERT INTO PosProduct VALUES(1,131);
INSERT INTO PosProduct VALUES(1,132);
INSERT INTO PosProduct VALUES(1,133);
INSERT INTO PosProduct VALUES(1,134);
INSERT INTO PosProduct VALUES(3,134);
INSERT INTO PosProduct VALUES(1,135);
INSERT INTO PosProduct VALUES(3,135);
INSERT INTO PosProduct VALUES(1,136);
INSERT INTO PosProduct VALUES(3,136);
INSERT INTO PosProduct VALUES(1,137);
INSERT INTO PosProduct VALUES(3,137);
INSERT INTO PosProduct VALUES(1,138);
INSERT INTO PosProduct VALUES(3,138);
INSERT INTO PosProduct VALUES(1,139);
INSERT INTO PosProduct VALUES(3,139);
INSERT INTO PosProduct VALUES(1,140);
INSERT INTO PosProduct VALUES(3,140);
INSERT INTO PosProduct VALUES(1,141);
INSERT INTO PosProduct VALUES(3,141);
INSERT INTO PosProduct VALUES(1,142);
INSERT INTO PosProduct VALUES(3,142);
INSERT INTO PosProduct VALUES(5,1);
INSERT INTO PosProduct VALUES(5,7);
INSERT INTO PosProduct VALUES(5,8);
INSERT INTO PosProduct VALUES(5,9);
INSERT INTO PosProduct VALUES(5,10);
INSERT INTO PosProduct VALUES(5,11);
INSERT INTO PosProduct VALUES(5,12);
INSERT INTO PosProduct VALUES(5,13);
INSERT INTO PosProduct VALUES(5,14);
INSERT INTO PosProduct VALUES(5,15);
INSERT INTO PosProduct VALUES(5,16);
INSERT INTO PosProduct VALUES(5,17);
INSERT INTO PosProduct VALUES(5,18);
INSERT INTO PosProduct VALUES(5,19);
INSERT INTO PosProduct VALUES(5,20);
INSERT INTO PosProduct VALUES(5,21);
INSERT INTO PosProduct VALUES(5,138);
INSERT INTO PosProduct VALUES(5,2);
INSERT INTO PosProduct VALUES(5,22);
INSERT INTO PosProduct VALUES(5,23);
INSERT INTO PosProduct VALUES(5,24);
INSERT INTO PosProduct VALUES(5,25);
INSERT INTO PosProduct VALUES(5,26);
INSERT INTO PosProduct VALUES(5,27);
INSERT INTO PosProduct VALUES(5,28);
INSERT INTO PosProduct VALUES(5,29);
INSERT INTO PosProduct VALUES(5,30);
INSERT INTO PosProduct VALUES(5,31);
INSERT INTO PosProduct VALUES(5,4);
INSERT INTO PosProduct VALUES(5,32);
INSERT INTO PosProduct VALUES(1,143);
INSERT INTO PosProduct VALUES(5,143);
INSERT INTO PosProduct VALUES(5,33);
INSERT INTO PosProduct VALUES(5,35);
INSERT INTO PosProduct VALUES(5,36);
INSERT INTO PosProduct VALUES(5,37);
INSERT INTO PosProduct VALUES(5,38);
INSERT INTO PosProduct VALUES(5,40);
INSERT INTO PosProduct VALUES(5,41);
INSERT INTO PosProduct VALUES(5,42);
INSERT INTO PosProduct VALUES(5,43);
INSERT INTO PosProduct VALUES(5,44);
INSERT INTO PosProduct VALUES(5,45);
INSERT INTO PosProduct VALUES(5,46);
INSERT INTO PosProduct VALUES(5,47);
INSERT INTO PosProduct VALUES(5,48);
INSERT INTO PosProduct VALUES(5,49);
INSERT INTO PosProduct VALUES(5,50);
INSERT INTO PosProduct VALUES(5,51);
INSERT INTO PosProduct VALUES(5,52);
INSERT INTO PosProduct VALUES(5,53);
INSERT INTO PosProduct VALUES(5,54);
INSERT INTO PosProduct VALUES(5,55);
INSERT INTO PosProduct VALUES(5,56);
INSERT INTO PosProduct VALUES(5,57);
INSERT INTO PosProduct VALUES(5,58);
INSERT INTO PosProduct VALUES(5,59);
INSERT INTO PosProduct VALUES(5,60);
INSERT INTO PosProduct VALUES(5,61);
INSERT INTO PosProduct VALUES(5,62);
INSERT INTO PosProduct VALUES(5,63);
INSERT INTO PosProduct VALUES(5,64);
INSERT INTO PosProduct VALUES(5,65);
INSERT INTO PosProduct VALUES(5,67);
INSERT INTO PosProduct VALUES(5,72);
INSERT INTO PosProduct VALUES(5,76);
INSERT INTO PosProduct VALUES(5,79);
INSERT INTO PosProduct VALUES(5,81);
INSERT INTO PosProduct VALUES(5,90);
INSERT INTO PosProduct VALUES(1,144);
INSERT INTO PosProduct VALUES(5,91);
INSERT INTO PosProduct VALUES(5,92);
INSERT INTO PosProduct VALUES(5,94);
INSERT INTO PosProduct VALUES(5,96);
INSERT INTO PosProduct VALUES(5,117);
INSERT INTO PosProduct VALUES(1,145);
INSERT INTO PosProduct VALUES(5,118);
INSERT INTO PosProduct VALUES(1,146);
INSERT INTO PosProduct VALUES(5,119);
INSERT INTO PosProduct VALUES(5,120);
INSERT INTO PosProduct VALUES(5,142);
INSERT INTO PosProduct VALUES(5,3);
INSERT INTO PosProduct VALUES(5,5);
INSERT INTO PosProduct VALUES(5,75);
INSERT INTO PosProduct VALUES(5,89);
INSERT INTO PosProduct VALUES(5,93);
INSERT INTO PosProduct VALUES(1,147);
INSERT INTO PosProduct VALUES(5,95);
INSERT INTO PosProduct VALUES(5,97);
INSERT INTO PosProduct VALUES(5,98);
INSERT INTO PosProduct VALUES(5,99);
INSERT INTO PosProduct VALUES(5,100);
INSERT INTO PosProduct VALUES(1,148);
INSERT INTO PosProduct VALUES(5,102);
INSERT INTO PosProduct VALUES(5,104);
INSERT INTO PosProduct VALUES(5,105);
INSERT INTO PosProduct VALUES(5,6);
INSERT INTO PosProduct VALUES(5,101);
INSERT INTO PosProduct VALUES(5,103);
INSERT INTO PosProduct VALUES(5,106);
INSERT INTO PosProduct VALUES(5,109);
INSERT INTO PosProduct VALUES(5,110);
INSERT INTO PosProduct VALUES(5,111);
INSERT INTO PosProduct VALUES(5,112);
INSERT INTO PosProduct VALUES(5,114);
INSERT INTO PosProduct VALUES(5,116);
INSERT INTO PosProduct VALUES(5,66);
INSERT INTO PosProduct VALUES(5,68);
INSERT INTO PosProduct VALUES(5,71);
INSERT INTO PosProduct VALUES(5,107);
INSERT INTO PosProduct VALUES(5,108);
INSERT INTO PosProduct VALUES(5,113);
INSERT INTO PosProduct VALUES(5,115);
INSERT INTO PosProduct VALUES(5,69);
INSERT INTO PosProduct VALUES(5,70);
INSERT INTO PosProduct VALUES(5,73);
INSERT INTO PosProduct VALUES(1,149);
INSERT INTO PosProduct VALUES(5,74);
INSERT INTO PosProduct VALUES(5,77);
INSERT INTO PosProduct VALUES(1,150);
INSERT INTO PosProduct VALUES(5,78);
INSERT INTO PosProduct VALUES(5,80);
INSERT INTO PosProduct VALUES(5,84);
INSERT INTO PosProduct VALUES(5,86);
INSERT INTO PosProduct VALUES(5,88);
INSERT INTO PosProduct VALUES(5,134);
INSERT INTO PosProduct VALUES(5,135);
INSERT INTO PosProduct VALUES(1,151);
INSERT INTO PosProduct VALUES(5,136);
INSERT INTO PosProduct VALUES(5,137);
INSERT INTO PosProduct VALUES(5,139);
INSERT INTO PosProduct VALUES(5,140);
INSERT INTO PosProduct VALUES(5,141);
INSERT INTO PosProduct VALUES(1,152);
INSERT INTO PosProduct VALUES(1,153);
INSERT INTO PosProduct VALUES(1,154);
INSERT INTO PosProduct VALUES(1,155);
INSERT INTO PosProduct VALUES(1,156);
INSERT INTO PosProduct VALUES(1,157);
INSERT INTO PosProduct VALUES(1,158);
INSERT INTO PosProduct VALUES(1,159);
INSERT INTO PosProduct VALUES(3,159);
INSERT INTO PosProduct VALUES(5,159);
INSERT INTO PosProduct VALUES(1,160);
INSERT INTO PosProduct VALUES(3,160);
INSERT INTO PosProduct VALUES(5,160);
INSERT INTO PosProduct VALUES(1,161);
INSERT INTO PosProduct VALUES(3,161);
INSERT INTO PosProduct VALUES(5,161);
INSERT INTO PosProduct VALUES(1,162);
INSERT INTO PosProduct VALUES(3,162);
INSERT INTO PosProduct VALUES(5,162);
COMMIT;