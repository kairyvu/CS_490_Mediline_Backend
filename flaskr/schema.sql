SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS doctor_patient_system;
CREATE SCHEMA doctor_patient_system DEFAULT CHARACTER SET utf8;
USE doctor_patient_system;


-- User is used to mainly handle social media page
CREATE TABLE user (
	user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(255) NOT NULL,
	password VARCHAR(255),
	account_type ENUM('doctor', 'patient', 'pharmacy', 'super_user') NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Super user doesn't need to have a name or address (it's more like a group of users that have the privilege to access the system).
CREATE TABLE super_user (
	super_user_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Notification tab which notify user about the upcomming events
CREATE TABLE notification (
	notification_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	notification_content TEXT,
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);


-- Doctor information
CREATE TABLE doctor (
	user_id INT PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	email VARCHAR(100) NOT NULL,
	phone VARCHAR(20) NOT NULL,
	specialization VARCHAR(100) NOT NULL,
	bio TEXT,
	fees DECIMAL(10,2) NOT NULL,
	profile_Image VARCHAR(255),
	dob DATE NOT NULL,
	license_id VARCHAR(50) NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Patient information
CREATE TABLE patient (
	user_id INT PRIMARY KEY,
	last_name VARCHAR(255) NOT NULL,
	first_name VARCHAR(255) NOT NULL,
	dob DATE NOT NULL,
	email VARCHAR(255) NOT NULL,
	phone_number VARCHAR(20),
	doctor_id INT NOT NULL,
	pharmacy_id INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE,
	FOREIGN KEY (pharmacy_id) REFERENCES pharmacy(user_id) ON DELETE CASCADE,
);

-- Appointment references to the doctor and patient (participants of a specific meeting)
CREATE TABLE appointment (
	appointment_id INT PRIMARY KEY AUTO_INCREMENT,
	doctor_id INT NOT NULL,
	patient_id INT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE
);

-- Storing appointment details such as (start date, end date, status)
CREATE TABLE appointment_detail (
	appointment_detail_id INT PRIMARY KEY AUTO_INCREMENT,
	appointment_id INT NOT NULL,
	start_date TIMESTAMP NOT NULL,
	end_date TIMESTAMP,
	status ENUM('approved', 'pending', 'canceled', 'completed') NOT NULL DEFAULT 'pending',
	FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
);

-- Patient medical record
CREATE TABLE medical_record (
	medical_record_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_id INT NOT NULL,
	description TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE
);

-- Prescription table can be used to fetch the doctor who prescribed the medication and the patient who is taking the medication
CREATE TABLE prescription (
	prescription_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_id INT NOT NULL,
	doctor_id INT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE
);

-- The table contains the dosage and medical instructions for the medication
CREATE TABLE prescription_medication (
	prescription_Medication_id INT PRIMARY KEY AUTO_INCREMENT,
	prescription_id INT NOT NULL,
	medication_id INT NOT NULL,
	dosage VARCHAR(100),
	medical_instructions TEXT,
	FOREIGN KEY (prescription_id) REFERENCES prescription(prescription_id),
	FOREIGN KEY (medication_id) REFERENCES medication(medication_id)
);

-- Survey types
CREATE TABLE survey (
	survey_id INT PRIMARY KEY AUTO_INCREMENT,
	Type ENUM('weekly', 'daily', 'monthly') NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Identify who is taking the survey and who is their doctor
CREATE TABLE patient_survey (
	patient_survey_id INT PRIMARY KEY AUTO_INCREMENT,
	survey_id INT NOT NULL,
	patient_id INT NOT NULL,
	doctor_id INT NOT NULL,
	FOREIGN KEY (survey_id) REFERENCES survey(survey_id) ON DELETE CASCADE,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE
);

-- All information that a patient needs to provide in the survey
CREATE TABLE survey_detail (
	survey_detail_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_survey_id INT NOT NULL,
	height FLOAT,
	weight FLOAT,
	calories_intake INT,
	hours_of_exercise INT,
	hours_of_sleep INT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (patient_survey_id) REFERENCES patient_survey(patient_survey_id)
);

-- Patient and doctor invoice
CREATE TABLE invoice (
	invoice_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_id INT NOT NULL,
	doctor_id INT NOT NULL,
	status ENUM('Paid', 'Pending') NOT NULL,
	pay_date DATE,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE
);

-- List of exercises 
CREATE TABLE exercise_bank (
	exercise_id INT PRIMARY KEY AUTO_INCREMENT,
	type_of_exercise VARCHAR(100) NOT NULL,
	description TEXT
);

-- Exercises that are assigned to a specific patient
CREATE TABLE patient_exercise (
	patient_exercise_id INT PRIMARY KEY AUTO_INCREMENT,
	exercise_id INT NOT NULL,
	patient_id INT NOT NULL,
	doctor_id INT NOT NULL,
	reps VARCHAR(30),
	Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (exercise_id) REFERENCES exercise_bank(exercise_id),
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE CASCADE,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE CASCADE
);

-- List of posts
CREATE TABLE post (
	post_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT NOT NULL,
	title VARCHAR(255),
	content TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- List of comments
CREATE TABLE comment (
	comment_id INT PRIMARY KEY AUTO_INCREMENT,
	post_id INT NOT NULL,
	user_id INT NOT NULL,
	content TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (post_id) REFERENCES post(post_id),
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);


-- Chat table to store the chat messages (during meeting between doctor and patient)
CREATE TABLE chat (
	chat_id INT PRIMARY KEY AUTO_INCREMENT,
	appointment_id INT NOT NULL,
	start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	end_date TIMESTAMP DEFAULT NULL,
	FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
);

-- Identify each messages in the chat
CREATE TABLE message (
	message_id INT PRIMARY KEY AUTO_INCREMENT,
	chat_id INT NOT NULL,
	user_id INT NOT NULL,
	message_content TEXT,
	time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (chat_id) REFERENCES chat(chat_id),
	FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Pharmacy information
CREATE TABLE pharmacy (
	user_id INT PRIMARY KEY,
	pharmacy_name VARCHAR(255) NOT NULL,
	phone VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	hours VARCHAR(255) NOT NULL,
	zip_code VARCHAR(255) NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Payment between patient and pharmacy
CREATE TABLE payment_prescription (
	payment_prescription_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	prescription_id INT NOT NULL,
	amount DECIMAL(4,2) NOT NULL,
	FOREIGN KEY (prescription_id) REFERENCES prescription(prescription_id) ON UPDATE RESTRICT ON DELETE CASCADE
);

-- List of all medications
CREATE TABLE medication (
	medication_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(25) NOT NULL,
	description TEXT
);

-- Inventory of the pharmacy
CREATE TABLE inventory (
	inventory_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	pharmacy_id INT NOT NULL,
	medication_id INT NOT NULL,
	stock INT DEFAULT 0,
	FOREIGN KEY (pharmacy_id) REFERENCES pharmacy(user_id) ON UPDATE RESTRICT ON DELETE CASCADE,
	FOREIGN KEY (medication_id) REFERENCES medication(medication_id) ON UPDATE RESTRICT ON DELETE CASCADE
);

-- Each record of rating that a patient gives to a doctor
CREATE TABLE rating_survey (
	survey_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_id INT NOT NULL,
	doctor_id INT NOT NULL,
	comment VARCHAR(255),
	stars DECIMAL(10,1),
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	FOREIGN KEY (patient_id) REFERENCES patient(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Fetch the rating record for a specific doctor
CREATE TABLE rating_record (
	rating_record_id INT PRIMARY KEY AUTO_INCREMENT,
	doctor_id INT NOT NULL,
	survey_id INT NOT NULL,
	FOREIGN KEY (doctor_id) REFERENCES doctor(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	FOREIGN KEY (survey_id) REFERENCES rating_survey(survey_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Graph tat shows data collected from (doctor-patient) surveys 
CREATE TABLE progress_graph (
	progress_graph_id INT PRIMARY KEY AUTO_INCREMENT,
	patient_survey_id INT NOT NULL,
	FOREIGN KEY (patient_survey_id) REFERENCES patient_survey(patient_survey_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Audit table
CREATE TABLE user_audit (
	audit_id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT,
	username_old VARCHAR(255),
	username_new VARCHAR(255),
	password_old VARCHAR(255),
	password_new VARCHAR(255),
	account_type_old ENUM('doctor', 'patient', 'pharmacy', 'super_user'),
	account_type_new ENUM('doctor', 'patient', 'pharmacy', 'super_user'),
	created_at_old TIMESTAMP,
	created_at_new TIMESTAMP,
	updated_at_old TIMESTAMP,
	updated_at_new TIMESTAMP,
	action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
	audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	audit_user VARCHAR(255)
);

-- Trigger for user table
DELIMITER //
CREATE TRIGGER user_audit_trigger
AFTER UPDATE ON user
FOR EACH ROW
BEGIN
	INSERT INTO user_audit (user_id, username_old, username_new, password_old, password_new, account_type_old, account_type_new, created_at_old, created_at_new, updated_at_old, updated_at_new, action, audit_user)
	VALUES (OLD.user_id, OLD.username, NEW.username, OLD.password, NEW.password, OLD.account_type, NEW.account_type, OLD.created_at, NEW.created_at, OLD.updated_at, NEW.updated_at, 'UPDATE', current_user());
END //

CREATE TRIGGER user_audit_insert_trigger
AFTER INSERT ON user
FOR EACH ROW
BEGIN
	INSERT INTO user_audit (user_id, username_new, password_new, account_type_new, created_at_new, updated_at_new, action, audit_user)
	VALUES (NEW.user_id, NEW.username, NEW.password, NEW.account_type, NEW.created_at, NEW.updated_at, 'INSERT', current_user());
END //

CREATE TRIGGER user_audit_delete_trigger
AFTER DELETE ON user
FOR EACH ROW
BEGIN
	INSERT INTO user_audit (user_id, username_old, password_old, account_type_old, created_at_old, updated_at_old, action, audit_user)
	VALUES (OLD.user_id, OLD.username, OLD.password, OLD.account_type, OLD.created_at, OLD.updated_at, 'DELETE', current_user());
END //
DELIMITER ;

-- Audit Table for doctor
CREATE TABLE doctor_audit (
	audit_id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT,
	first_name_old VARCHAR(50),
	first_name_new VARCHAR(50),
	last_name_old VARCHAR(50),
	last_name_new VARCHAR(50),
	email_old VARCHAR(100),
	email_new VARCHAR(100),
	phone_old VARCHAR(20),
	phone_new VARCHAR(20),
	specialization_old VARCHAR(100),
	specialization_new VARCHAR(100),
	bio_old TEXT,
	bio_new TEXT,
	fees_old DECIMAL(10,2),
	fees_new DECIMAL(10,2),
	profile_Image_old VARCHAR(255),
	profile_Image_new VARCHAR(255),
	dob_old DATE,
	dob_new DATE,
	license_id_old VARCHAR(50),
	license_id_new VARCHAR(50),
	action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
	audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	audit_user VARCHAR(255)
);

-- Trigger for doctor table
DELIMITER //
CREATE TRIGGER doctor_audit_trigger
AFTER UPDATE ON doctor
FOR EACH ROW
BEGIN
	INSERT INTO doctor_audit (user_id, first_name_old, first_name_new, last_name_old, last_name_new, email_old, email_new, phone_old, phone_new, specialization_old, specialization_new, bio_old, bio_new, fees_old, fees_new, profile_Image_old, profile_Image_new, dob_old, dob_new, license_id_old, license_id_new, action, audit_user)
	VALUES (OLD.user_id, OLD.first_name, NEW.first_name, OLD.last_name, NEW.last_name, OLD.email, NEW.email, OLD.phone, NEW.phone, OLD.specialization, NEW.specialization, OLD.bio, NEW.bio, OLD.fees, NEW.fees, OLD.profile_Image, NEW.profile_Image, OLD.dob, NEW.dob, OLD.license_id, NEW.license_id, 'UPDATE', current_user());
END //

CREATE TRIGGER doctor_audit_insert_trigger
AFTER INSERT ON doctor
FOR EACH ROW
BEGIN
	INSERT INTO doctor_audit (user_id, first_name_new, last_name_new, email_new, phone_new, specialization_new, bio_new, fees_new, profile_Image_new, dob_new, license_id_new, action, audit_user)
	VALUES (NEW.user_id, NEW.first_name, NEW.last_name, NEW.email, NEW.phone, NEW.specialization, NEW.bio, NEW.fees, NEW.profile_Image, NEW.dob, NEW.license_id, 'INSERT', current_user());
END //

CREATE TRIGGER doctor_audit_delete_trigger
AFTER DELETE ON doctor
FOR EACH ROW
BEGIN
	INSERT INTO doctor_audit (user_id, first_name_old, last_name_old, email_old, phone_old, specialization_old, bio_old, fees_old, profile_Image_old, dob_old, license_id_old, action, audit_user)
	VALUES (OLD.user_id, OLD.first_name, OLD.last_name, OLD.email, OLD.phone, OLD.specialization, OLD.bio, OLD.fees, OLD.profile_Image, OLD.dob, OLD.license_id, 'DELETE', current_user());
END //
DELIMITER ;


-- Audit Table for patient
CREATE TABLE patient_audit (
	audit_id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT,
	last_name_old VARCHAR(255),
	last_name_new VARCHAR(255),
	first_name_old VARCHAR(255),
	first_name_new VARCHAR(255),
	dob_old DATE,
	dob_new DATE,
	email_old VARCHAR(255),
	email_new VARCHAR(255),
	phone_number_old VARCHAR(20),
	phone_number_new VARCHAR(20),
	doctor_id_old INT,
	doctor_id_new INT,
	pharmacy_id_old INT,
	pharmacy_id_new INT,
	action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
	audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	audit_user VARCHAR(255)
);

-- Trigger for patient table
DELIMITER //
CREATE TRIGGER patient_audit_trigger
AFTER UPDATE ON patient
FOR EACH ROW
BEGIN
	INSERT INTO patient_audit (user_id, last_name_old, last_name_new, first_name_old, first_name_new, dob_old, dob_new, email_old, email_new, phone_number_old, phone_number_new, doctor_id_old, doctor_id_new, pharmacy_id_old, pharmacy_id_new, action, audit_user)
	VALUES (OLD.user_id, OLD.last_name, NEW.last_name, OLD.first_name, NEW.first_name, OLD.dob, NEW.dob, OLD.email, NEW.email, OLD.phone_number, NEW.phone_number, OLD.doctor_id, NEW.doctor_id, OLD.pharmacy_id, NEW.pharmacy_id, 'UPDATE', current_user());
END //

CREATE TRIGGER patient_audit_insert_trigger
AFTER INSERT ON patient
FOR EACH ROW
BEGIN
	INSERT INTO patient_audit (user_id, last_name_new, first_name_new, dob_new, email_new, phone_number_new, doctor_id_new, pharmacy_id_new, action, audit_user)
	VALUES (NEW.user_id, NEW.last_name, NEW.first_name, NEW.dob, NEW.email, NEW.phone_number, NEW.doctor_id, NEW.pharmacy_id, 'INSERT', current_user());
END //

CREATE TRIGGER patient_audit_delete_trigger
AFTER DELETE ON patient
FOR EACH ROW
BEGIN
	INSERT INTO patient_audit (user_id, last_name_old, first_name_old, dob_old, email_old, phone_number_old, doctor_id_old, pharmacy_id_old, action, audit_user)
	VALUES (OLD.user_id, OLD.last_name, OLD.first_name, OLD.dob, OLD.email, OLD.phone_number, OLD.doctor_id, OLD.pharmacy_id, 'DELETE', current_user());
END //
DELIMITER ;

-- Audit Table for appointment
CREATE TABLE appointment_audit (
	audit_id INT AUTO_INCREMENT PRIMARY KEY,
	appointment_id INT,
	doctor_id_old INT,
	doctor_id_new INT,
	patient_id_old INT,
	patient_id_new INT,
	created_at_old TIMESTAMP,
	created_at_new TIMESTAMP,
	last_updated_old TIMESTAMP,
	last_updated_new TIMESTAMP,
	action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
	audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	audit_user VARCHAR(255)
);

-- Trigger for appointment table
DELIMITER //
CREATE TRIGGER appointment_audit_trigger
AFTER UPDATE ON appointment
FOR EACH ROW
BEGIN
	INSERT INTO appointment_audit (appointment_id, doctor_id_old, doctor_id_new, patient_id_old, patient_id_new, created_at_old, created_at_new, last_updated_old, last_updated_new, action, audit_user)
	VALUES (OLD.appointment_id, OLD.doctor_id, NEW.doctor_id, OLD.patient_id, NEW.patient_id, OLD.created_at, NEW.created_at, OLD.last_updated, NEW.last_updated, 'UPDATE', current_user());
END //

CREATE TRIGGER appointment_audit_insert_trigger
AFTER INSERT ON appointment
FOR EACH ROW
BEGIN
	INSERT INTO appointment_audit (appointment_id, doctor_id_new, patient_id_new, created_at_new, last_updated_new, action, audit_user)
	VALUES (NEW.appointment_id, NEW.doctor_id, NEW.patient_id, NEW.created_at, NEW.last_updated, 'INSERT', current_user());
END //

CREATE TRIGGER appointment_audit_delete_trigger
AFTER DELETE ON appointment
FOR EACH ROW
BEGIN
	INSERT INTO appointment_audit (appointment_id, doctor_id_old, patient_id_old, created_at_old, last_updated_old, action)
	VALUES (OLD.appointment_id, OLD.doctor_id, OLD.patient_id, OLD.created_at, OLD.last_updated, 'DELETE', current_user());
END //
DELIMITER ;