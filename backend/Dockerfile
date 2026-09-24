# Compila com a mesma versão do toolchain do Gradle (ADR-0003).
FROM eclipse-temurin:25-jdk-noble AS build
WORKDIR /app
COPY gradle gradle
COPY gradlew settings.gradle.kts build.gradle.kts ./
RUN ./gradlew --no-daemon dependencies -q || true
COPY src src
RUN ./gradlew --no-daemon bootJar -x test

FROM eclipse-temurin:25-jre-noble
WORKDIR /app
# curl serve à verificação de saúde do contêiner; a imagem JRE não traz cliente HTTP.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
# Sem privilégio: o processo não precisa de root para servir HTTP.
RUN useradd --system --uid 10001 app
COPY --from=build /app/build/libs/*.jar app.jar
USER app
EXPOSE 8080
# O limite de memória do contêiner é quem manda, não 25% da memória do host.
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=70"
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
