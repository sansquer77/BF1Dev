PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha_hash TEXT,
        perfil TEXT,
        status TEXT DEFAULT 'Ativo',
        faltas INTEGER DEFAULT 0
    );
INSERT INTO usuarios VALUES(3,'Administrator','bote_album11@icloud.com','$2b$12$KoKc.bxZq4Ov3k/WP5Ss7uQuKbGOnLVXPXljS3FYzptNtqGKcp1TO','master','Ativo',0);
CREATE TABLE pilotos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        equipe TEXT,
        status TEXT DEFAULT 'Ativo'
    );
INSERT INTO pilotos VALUES(1,'Pierre Gasly','Alpine','Ativo');
INSERT INTO pilotos VALUES(2,'Jack Doohan','Alpine','Inativo');
INSERT INTO pilotos VALUES(3,'Fernando Alonso','Aston Martin','Ativo');
INSERT INTO pilotos VALUES(4,'Lance Stroll','Aston Martin','Ativo');
INSERT INTO pilotos VALUES(5,'Charles Leclerc','Ferrari','Ativo');
INSERT INTO pilotos VALUES(6,'Lewis Hamilton','Ferrari','Ativo');
INSERT INTO pilotos VALUES(7,'Esteban Ocon','Haas','Ativo');
INSERT INTO pilotos VALUES(8,'Oliver Bearman','Haas','Ativo');
INSERT INTO pilotos VALUES(9,'Lando Norris','McLaren','Ativo');
INSERT INTO pilotos VALUES(10,'Oscar Piastri','McLaren','Ativo');
INSERT INTO pilotos VALUES(11,'Kimi Antonelli','Mercedes','Ativo');
INSERT INTO pilotos VALUES(12,'George Russell','Mercedes','Ativo');
INSERT INTO pilotos VALUES(13,'Liam Lawson','Racing Bulls','Ativo');
INSERT INTO pilotos VALUES(14,'Isack Hadjar','Racing Bulls','Ativo');
INSERT INTO pilotos VALUES(15,'Max Verstappen','Red Bull','Ativo');
INSERT INTO pilotos VALUES(16,'Yuki Tsunoda','Red Bull','Ativo');
INSERT INTO pilotos VALUES(17,'Nico Hülkenberg','Sauber','Ativo');
INSERT INTO pilotos VALUES(18,'Gabriel Bortoleto','Sauber','Ativo');
INSERT INTO pilotos VALUES(19,'Alex Albon','Williams','Ativo');
INSERT INTO pilotos VALUES(20,'Carlos Sainz','Williams','Ativo');
INSERT INTO pilotos VALUES(21,'Franco Colapinto','Alpine','Ativo');
CREATE TABLE provas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data TEXT,
        horario_prova TEXT,
        status TEXT DEFAULT 'Ativo',
        tipo TEXT DEFAULT 'Normal'
    );
INSERT INTO provas VALUES(1,'Grande Prêmio da Austrália','2025-03-16','01:00:00','Ativo','Normal');
INSERT INTO provas VALUES(2,'Grande Prêmio da China Sprint','2025-03-22','00:00:00','Ativo','Sprint');
INSERT INTO provas VALUES(3,'Grande Prêmio da China','2025-03-23','04:00:00','Ativo','Normal');
INSERT INTO provas VALUES(4,'Grande Prêmio do Japão','2025-04-06','02:00:00','Ativo','Normal');
INSERT INTO provas VALUES(5,'Grande Prêmio do Bahrain','2025-04-13','12:00:00','Ativo','Normal');
INSERT INTO provas VALUES(6,'Grande Prêmio da Arábia Saudita','2025-04-20','14:00:00','Ativo','Normal');
INSERT INTO provas VALUES(7,'Grande Prêmio de Miami Sprint','2025-05-03','13:00:00','Ativo','Sprint');
INSERT INTO provas VALUES(8,'Grande Prêmio de Miami','2025-05-04','17:00:00','Ativo','Normal');
INSERT INTO provas VALUES(9,'Grande Prêmio da Emília-Romanha','2025-05-18','10:00:00','Ativo','Normal');
INSERT INTO provas VALUES(10,'Grande Prêmio de Mônaco','2025-05-25','10:00:00','Ativo','Normal');
INSERT INTO provas VALUES(11,'Grande Prêmio da Espanha','2025-06-01','10:00:00','Ativo','Normal');
INSERT INTO provas VALUES(12,'Grande Prêmio do Canadá','2025-06-15','15:00:00','Ativo','Normal');
INSERT INTO provas VALUES(13,'Grande Prêmio da Áustria','2025-06-29','10:00:01','Ativo','Normal');
INSERT INTO provas VALUES(14,'Grande Prêmio da Grã-Bretanha','2025-07-06','11:00:01','Ativo','Normal');
INSERT INTO provas VALUES(15,'Grande Prêmio da Bélgica Sprint','2025-07-26','08:00:01','Ativo','Sprint');
INSERT INTO provas VALUES(16,'Grande Prêmio da Bélgica','2025-07-27','10:00:01','Ativo','Normal');
INSERT INTO provas VALUES(17,'Grande Prêmio da Hungria','2025-08-03','10:00:01','Ativo','Normal');
INSERT INTO provas VALUES(18,'Grande Prêmio dos Países Baixos','2025-08-31','10:00:01','Ativo','Normal');
INSERT INTO provas VALUES(19,'Grande Prêmio da Itália','2025-09-07','10:00:01','Ativo','Normal');
INSERT INTO provas VALUES(20,'Grande Prêmio do Azerbaijão','2025-09-21','08:00:01','Ativo','Normal');
INSERT INTO provas VALUES(21,'Grande Prêmio de Singapura','2025-10-05','09:00:01','Ativo','Normal');
INSERT INTO provas VALUES(22,'Grande Prêmio dos EUA Sprint','2025-10-18','15:00:01','Ativo','Sprint');
INSERT INTO provas VALUES(23,'Grande Prêmio dos EUA','2025-10-19','16:00:01','Ativo','Normal');
INSERT INTO provas VALUES(24,'Grande Prêmio da Cidade do México','2025-10-26','17:00:01','Ativo','Normal');
INSERT INTO provas VALUES(25,'Grande Prêmio de São Paulo Sprint','2025-11-08','11:00:01','Ativo','Sprint');
INSERT INTO provas VALUES(26,'Grande Prêmio de São Paulo','2025-11-09','14:00:01','Ativo','Normal');
INSERT INTO provas VALUES(27,'Grande Prêmio de Las Vegas','2025-11-23','01:00:01','Ativo','Normal');
INSERT INTO provas VALUES(28,'Grande Prêmio do Catar Sprint','2025-11-29','11:00:01','Ativo','Sprint');
INSERT INTO provas VALUES(29,'Grande Prêmio do Catar','2025-11-30','13:00:01','Ativo','Normal');
INSERT INTO provas VALUES(30,'Grande Prêmio de Abu Dhabi','2025-12-07','10:00:01','Ativo','Normal');
CREATE TABLE apostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        prova_id INTEGER,
        data_envio TEXT,
        pilotos TEXT,
        fichas TEXT,
        piloto_11 TEXT,
        nome_prova TEXT,
        automatica INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(prova_id) REFERENCES provas(id)
    );
INSERT INTO apostas VALUES(1,1,1,'2025-06-12T15:31:03.566437','Oscar Piastri,Max Verstappen,George Russell','7,7,1','Pierre Gasly','Grande Prêmio da Austrália',0);
INSERT INTO apostas VALUES(2,1,2,'2025-06-12T15:32:17.617071','Lewis Hamilton,Max Verstappen,George Russell,Oscar Piastri','6,6,2,1','Carlos Sainz','Grande Prêmio da China Sprint',0);
INSERT INTO apostas VALUES(3,1,3,'2025-06-12T15:33:31.166843','Oscar Piastri,Lewis Hamilton,George Russell,Max Verstappen','12,1,1,1','Pierre Gasly','Grande Prêmio da China',0);
INSERT INTO apostas VALUES(4,1,4,'2025-06-12T15:40:29.306774','Oscar Piastri,Max Verstappen,George Russell','13,1,1','Carlos Sainz','Grande Prêmio do Japão',0);
INSERT INTO apostas VALUES(5,1,5,'2025-06-12T15:41:36.236738','Oscar Piastri,George Russell,Charles Leclerc','13,1,1','Carlos Sainz','Grande Prêmio do Bahrain',0);
INSERT INTO apostas VALUES(6,1,6,'2025-06-12T15:43:20.116182','Oscar Piastri,George Russell,Max Verstappen','8,1,6','Isack Hadjar','Grande Prêmio da Arábia Saudita',0);
INSERT INTO apostas VALUES(7,1,7,'2025-06-12T15:44:18.525740','Oscar Piastri,Kimi Antonelli,Max Verstappen','13,1,1','Yuki Tsunoda','Grande Prêmio de Miami Sprint',0);
INSERT INTO apostas VALUES(8,1,8,'2025-06-12T15:46:51.405213','Oscar Piastri,Kimi Antonelli,Max Verstappen','13,1,1','Isack Hadjar','Grande Prêmio de Miami',0);
INSERT INTO apostas VALUES(9,1,9,'2025-06-12T15:48:10.898866','Oscar Piastri,George Russell,Max Verstappen','7,1,7','Lance Stroll','Grande Prêmio da Emília-Romanha',0);
INSERT INTO apostas VALUES(10,1,10,'2025-06-12T15:54:28.822341','Lando Norris,George Russell,Max Verstappen','13,1,1','Pierre Gasly','Grande Prêmio de Mônaco',0);
INSERT INTO apostas VALUES(11,1,11,'2025-06-12T15:55:20.874281','Oscar Piastri,George Russell,Max Verstappen','13,1,1','Esteban Ocon','Grande Prêmio da Espanha',0);
INSERT INTO apostas VALUES(13,99,12,'2025-06-14T21:30:09.965642','Oscar Piastri,George Russell,Max Verstappen','5,5,5','Yuki Tsunoda','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(14,1,12,'2025-06-14T21:43:38.114164','Oscar Piastri,Max Verstappen,George Russell','1,13,1','Nico Hülkenberg','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(15,50,12,'2025-06-14T22:23:43.735490','Max Verstappen,George Russell,Oscar Piastri','13,1,1','Alex Albon','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(16,320,12,'2025-06-15T13:36:28.061408','Oscar Piastri,Max Verstappen,George Russell','11,3,1','Nico Hülkenberg','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(18,408,12,'2025-06-15T16:16:53.373857','Oscar Piastri,George Russell,Max Verstappen','13,1,1','Isack Hadjar','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(19,339,12,'2025-06-15T16:19:43.520717','George Russell,Max Verstappen,Oscar Piastri','5,3,7','Yuki Tsunoda','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(20,74,12,'2025-06-15T16:49:09.231864','Oscar Piastri,Max Verstappen,George Russell','7,7,1','Isack Hadjar','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(23,2,12,'2025-06-15T19:55:02.516251-03:00','Oscar Piastri,George Russell,Max Verstappen','1,1,13','Nico Hülkenberg','Grande Prêmio do Canadá',0);
INSERT INTO apostas VALUES(27,99,2,'2025-06-16T10:28:01.625015-03:00','Lewis Hamilton,Oscar Piastri,Max Verstappen','5,5,5','Lance Stroll','Grande Prêmio da China Sprint',0);
INSERT INTO apostas VALUES(29,99,3,'2025-06-16T10:31:05.169505-03:00','Lewis Hamilton,Lando Norris,George Russell,Max Verstappen','3,5,2,5','Esteban Ocon','Grande Prêmio da China',0);
INSERT INTO apostas VALUES(30,99,4,'2025-06-16T10:32:29.993100-03:00','Charles Leclerc,Lando Norris,Max Verstappen','5,5,5','Alex Albon','Grande Prêmio do Japão',0);
INSERT INTO apostas VALUES(31,99,5,'2025-06-16T10:33:50.282970-03:00','Charles Leclerc,Oscar Piastri,Max Verstappen','2,11,2','Alex Albon','Grande Prêmio do Bahrain',0);
INSERT INTO apostas VALUES(32,99,6,'2025-06-16T10:35:01.708795-03:00','Charles Leclerc,Oscar Piastri,Max Verstappen','1,13,1','Alex Albon','Grande Prêmio da Arábia Saudita',0);
INSERT INTO apostas VALUES(33,99,7,'2025-06-16T10:39:02.991684-03:00','Oscar Piastri,Kimi Antonelli,Max Verstappen','13,1,1','Fernando Alonso','Grande Prêmio de Miami Sprint',0);
INSERT INTO apostas VALUES(34,99,8,'2025-06-16T10:41:24.392746-03:00','Lando Norris,George Russell,Max Verstappen','1,1,13','Fernando Alonso','Grande Prêmio de Miami',0);
INSERT INTO apostas VALUES(35,99,10,'2025-06-16T10:43:56.558764-03:00','Charles Leclerc,Lando Norris,Max Verstappen','5,5,5','Alex Albon','Grande Prêmio de Mônaco',0);
INSERT INTO apostas VALUES(36,99,11,'2025-06-16T10:45:24.785045-03:00','Oscar Piastri,George Russell,Max Verstappen','13,1,1','Fernando Alonso','Grande Prêmio da Espanha',0);
INSERT INTO apostas VALUES(37,99,9,'2025-06-16T12:52:42.355518-03:00','Lando Norris,George Russell,Max Verstappen','1,1,13','Fernando Alonso','Grande Prêmio da Emília-Romanha',1);
INSERT INTO apostas VALUES(38,295,1,'2025-06-17T01:50:23.698678-03:00','Charles Leclerc,Max Verstappen,Lando Norris','1,13,1','Fernando Alonso','Grande Prêmio da Austrália',0);
/****** CORRUPTION ERROR *******/
CREATE TABLE resultados (
        prova_id INTEGER PRIMARY KEY,
        posicoes TEXT,
        FOREIGN KEY(prova_id) REFERENCES provas(id)
    );
/****** CORRUPTION ERROR *******/
CREATE TABLE posicoes_participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prova_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        posicao INTEGER NOT NULL,
        pontos REAL NOT NULL,
        data_registro TEXT DEFAULT (datetime('now')),
        UNIQUE(prova_id, usuario_id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (prova_id) REFERENCES provas(id)
    );
INSERT INTO posicoes_participantes VALUES(8450,1,99,1,358.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8451,1,973,2,341.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8452,1,320,3,323.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8453,1,928,4,320.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8454,1,163,5,317.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8455,1,50,6,316.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8456,1,295,7,263.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8457,1,527,8,263.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8458,1,2,9,260.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8459,1,152,10,220.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8460,1,388,11,193.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8461,1,1,12,180.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8462,1,3,13,162.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8463,1,408,14,149.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8464,1,339,15,123.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8465,1,74,16,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8466,1,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8467,2,152,1,117.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8468,2,408,2,107.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8469,2,339,3,106.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8470,2,2,4,105.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8471,2,99,5,105.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8472,2,320,6,105.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8473,2,163,7,104.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8474,2,1,8,101.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8475,2,3,9,100.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8476,2,74,10,100.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8477,2,50,11,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8478,2,295,12,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8479,2,527,13,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8480,2,388,14,75.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8481,2,928,15,48.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8482,2,973,16,33.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8483,2,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8484,3,50,1,337.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8485,3,1,2,327.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8486,3,339,3,326.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8487,3,527,4,322.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8488,3,163,5,306.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8489,3,2,6,305.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8490,3,295,7,261.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8491,3,408,8,260.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8492,3,74,9,225.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8493,3,973,10,219.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8494,3,320,11,197.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8495,3,99,12,180.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8496,3,152,13,173.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8497,3,3,14,165.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8498,3,388,15,156.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8499,3,928,16,135.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8500,3,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8501,4,50,1,353.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8502,4,74,2,311.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8503,4,928,3,290.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8504,4,320,4,282.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8505,4,163,5,281.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8506,4,408,6,281.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8507,4,99,7,275.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8508,4,973,8,274.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8509,4,2,9,271.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8510,4,3,10,271.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8511,4,152,11,271.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8512,4,295,12,271.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8513,4,339,13,268.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8514,4,388,14,250.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8515,4,527,15,232.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8516,4,1,16,230.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8517,4,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8518,5,1,1,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8519,5,2,2,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8520,5,50,3,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8521,5,152,4,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8522,5,295,5,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8523,5,527,6,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8524,5,973,7,355.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8525,5,74,8,351.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8526,5,339,9,351.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8527,5,408,10,351.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8528,5,163,11,348.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8529,5,99,12,315.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8530,5,320,13,303.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8531,5,3,14,257.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8532,5,388,15,213.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8533,5,928,16,153.75,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8534,5,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8535,6,152,1,378.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8536,6,99,2,358.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8537,6,2,3,353.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8538,6,50,4,353.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8539,6,295,5,353.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8540,6,408,6,353.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8541,6,163,7,325.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8542,6,973,8,325.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8543,6,1,9,318.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8544,6,3,10,311.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8545,6,74,11,297.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8546,6,339,12,297.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8547,6,928,13,294.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8548,6,320,14,269.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8549,6,527,15,269.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8550,6,388,16,164.25,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8551,6,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8552,7,295,1,99.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8553,7,339,2,94.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8554,7,1,3,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8555,7,2,4,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8556,7,50,5,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8557,7,74,6,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8558,7,99,7,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8559,7,152,8,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8560,7,320,9,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8561,7,408,10,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8562,7,973,11,93.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8563,7,527,12,91.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8564,7,163,13,78.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8565,7,3,14,70.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8566,7,928,15,45.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8567,7,388,16,40.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8568,7,553,17,0.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8569,8,1,1,370.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8570,8,527,2,352.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8571,8,163,3,294.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8572,8,408,4,286.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8573,8,74,5,243.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8574,8,3,6,240.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8575,8,320,7,236.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8576,8,973,8,236.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8577,8,339,9,215.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8578,8,50,10,214.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8579,8,388,11,198.0,'2025-12-06 23:21:11');
INSERT INTO posicoes_participantes VALUES(8580,8,99,12,189.0,'2025-12-06 23:21:11');
/****** CORRUPTION ERROR *******/
CREATE TABLE log_apostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apostador TEXT,
        data TEXT,
        horario TEXT,
        aposta TEXT,
        piloto_11 TEXT,
        nome_prova TEXT,
        tipo_aposta INTEGER DEFAULT 0,
        automatica INTEGER DEFAULT 0
    );
/****** CORRUPTION ERROR *******/
CREATE TABLE championship_bets (
        user_id INTEGER PRIMARY KEY,
        user_nome TEXT NOT NULL,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL,
        bet_time TEXT NOT NULL
    );
INSERT INTO championship_bets VALUES(1,'Cristiano Gaspar','Max Verstappen','Lando Norris','McLaren','2025-06-15 17:06:09');
INSERT INTO championship_bets VALUES(2,'Elton Santos','Max Verstappen','Lando Norris','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(3,'Rafael de Paula Gaspar','Lewis Hamilton','Max Verstappen','Ferrari','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(50,'Rafael Petherson Sampaio ','Lando Norris','Max Verstappen','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(74,'Matheus Lorran Silva','Max Verstappen','Oscar Piastri','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(99,'Antonio Carlos Rodrigues ','Lando Norris','Max Verstappen','McLaren','2025-06-17 11:31:43');
INSERT INTO championship_bets VALUES(152,'Leandro Aoki ','Lewis Hamilton','Max Verstappen','Ferrari','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(163,'Jose Carlos da Costa Lima Junior','Lando Norris','Oscar Piastri','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(295,'Thiago Fugita','Max Verstappen','Lando Norris','McLaren','2025-06-17 05:10:03');
INSERT INTO championship_bets VALUES(320,'Vitor Sakassegawa','Lando Norris','Max Verstappen','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(339,'Hamilton Hamamoto','Max Verstappen','Lando Norris','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(388,'Haroldo de Paula  Domingo','Charles Leclerc','Max Verstappen','Red Bull','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(408,'Odilon de Oliveira ','Oscar Piastri','Lando Norris','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(527,'Fabrício de Vasconcelos ','Max Verstappen','Lando Norris','McLaren','2025-06-22 18:45:00');
INSERT INTO championship_bets VALUES(928,'Carlos Eduardo de Sá','Lando Norris','Max Verstappen','McLaren','2025-06-29 00:21:24');
INSERT INTO championship_bets VALUES(973,'Fabio da Silva Lance ','Lewis Hamilton','Lando Norris','Ferrari','2025-06-29 00:21:24');
CREATE TABLE championship_bets_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_nome TEXT NOT NULL,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL,
        bet_time TEXT NOT NULL
    );
INSERT INTO championship_bets_log VALUES(8,'bote_album11@icloud.com','2025-12-07 03:22:20',1,'LOCAL',NULL,NULL);
INSERT INTO championship_bets_log VALUES(9,'bote_album11@icloud.com','2025-12-07 03:28:04',1,'LOCAL',NULL,NULL);
INSERT INTO championship_bets_log VALUES(10,'bote_album11@icloud.com','2025-12-07 03:28:28',1,'LOCAL',NULL,NULL);
CREATE TABLE championship_results (
        season INTEGER PRIMARY KEY DEFAULT 2025,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL
    );
/****** CORRUPTION ERROR *******/
INSERT INTO sqlite_sequence VALUES('login_attempts',10);
INSERT INTO sqlite_sequence VALUES('usuarios',3);
ROLLBACK; -- due to errors
