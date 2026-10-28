plugins {
    id("com.android.application")
}

android {
    namespace = "dev.astro.watchface"
    compileSdk = 34

    defaultConfig {
        applicationId = "dev.astro.watchface"
        minSdk = 33
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
