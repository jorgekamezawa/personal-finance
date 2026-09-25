package com.personalfinance.architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import java.math.BigDecimal;
import java.math.MathContext;
import org.junit.jupiter.api.Test;

class MoneyIsNeverBuiltFromDoubleTest {

    @Test
    void moneyIsNeverBuiltFromDouble() {
        JavaClasses production = new ClassFileImporter()
                .withImportOption(new ImportOption.DoNotIncludeTests())
                .importPackages("com.personalfinance");

        noClasses()
                .should()
                .callConstructor(BigDecimal.class, double.class)
                .orShould()
                .callConstructor(BigDecimal.class, double.class, MathContext.class)
                .check(production);
    }
}
