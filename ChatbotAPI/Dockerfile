FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore
COPY ["ChatbotAPI.csproj", "./"]
RUN dotnet restore "ChatbotAPI.csproj"

# Copy everything else and build
COPY . .
RUN dotnet build "ChatbotAPI.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ChatbotAPI.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Create uploads directory
RUN mkdir -p /app/uploads

ENTRYPOINT ["dotnet", "ChatbotAPI.dll"]

