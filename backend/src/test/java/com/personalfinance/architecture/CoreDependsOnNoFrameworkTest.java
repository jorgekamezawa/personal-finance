package com.personalfinance.architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.Test;

class CoreDependsOnNoFrameworkTest {

    private static final String[] FRAMEWORK_PACKAGES = {
        "org.springframework..", "jakarta..", "org.hibernate..", "tools.jackson..", "com.fasterxml.jackson.."
    };

    @Test
    void coreDependsOnNoFramework() {
        JavaClasses production = new ClassFileImporter()
                .withImportOption(new ImportOption.DoNotIncludeTests())
                .importPackages("com.personalfinance");

        noClasses()
                .that()
                .resideInAnyPackage("..domain..", "..shared.tipo..")
                .should()
                .dependOnClassesThat()
                .resideInAnyPackage(FRAMEWORK_PACKAGES)
                // Neither package exists yet, and ArchUnit fails a rule that matched no class at all.
                .allowEmptyShould(true)
                .check(production);
    }
}
