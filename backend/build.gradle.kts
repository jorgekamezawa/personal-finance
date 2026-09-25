import net.ltgt.gradle.errorprone.errorprone

plugins {
	java
	id("org.springframework.boot") version "4.1.1"
	id("io.spring.dependency-management") version "1.1.7"
	id("com.diffplug.spotless") version "8.10.2"
	id("net.ltgt.errorprone") version "5.1.1"
}

group = "com.personalfinance"
version = "0.0.1-SNAPSHOT"
description = "Personal finance backend"

java {
	toolchain {
		languageVersion = JavaLanguageVersion.of(25)
	}
}

repositories {
	mavenCentral()
}

dependencies {
	// Code analysis
	errorprone("com.google.errorprone:error_prone_core:2.50.0")

	// Web and operations
	implementation("org.springframework.boot:spring-boot-starter-webmvc")
	implementation("org.springframework.boot:spring-boot-starter-actuator")

	// Persistence
	implementation("org.springframework.boot:spring-boot-starter-data-jpa")
	runtimeOnly("org.postgresql:postgresql")

	// Testing
	testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
	testImplementation("org.springframework.boot:spring-boot-starter-actuator-test")
	testImplementation("org.springframework.boot:spring-boot-testcontainers")
	testImplementation("org.testcontainers:testcontainers-junit-jupiter")
	testImplementation("org.testcontainers:testcontainers-postgresql")
	testImplementation("com.tngtech.archunit:archunit:1.5.0")
}

// Palantir formats with 4 spaces and 120 columns, matching the code already written here.
spotless {
	java {
		palantirJavaFormat("2.99.0")
	}
}

// Without this, javac falls back to the platform encoding and non-ASCII sources break the build.
tasks.withType<JavaCompile> {
	options.encoding = "UTF-8"
	options.compilerArgs.add("-Xlint:all")
	options.errorprone {
		// Comparing or building money the wrong way changes an amount without failing anywhere.
		error("BigDecimalEquals", "BigDecimalLiteralDouble")
	}
}

tasks.withType<Test> {
	useJUnitPlatform()
}
