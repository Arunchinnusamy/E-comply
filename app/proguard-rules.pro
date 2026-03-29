# ─── Debugging: keep line numbers in stack traces ────────────────────────────
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# ─── Data / Model classes (Gson serialization) ───────────────────────────────
# Keep all data classes in the model and remote packages so Gson can
# serialize/deserialize them without reflection failures at runtime.
-keep class com.example.e_comply.data.model.** { *; }
-keep class com.example.e_comply.data.remote.** { *; }

# ─── Retrofit ────────────────────────────────────────────────────────────────
-keepattributes Signature
-keepattributes Exceptions
-keep class retrofit2.** { *; }
-keepclassmembernames interface * {
    @retrofit2.http.* <methods>;
}

# ─── OkHttp ──────────────────────────────────────────────────────────────────
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# ─── Gson ────────────────────────────────────────────────────────────────────
-keep class com.google.gson.** { *; }
-keepattributes *Annotation*

# ─── Firebase ────────────────────────────────────────────────────────────────
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.firebase.**
-dontwarn com.google.android.gms.**

# ─── Firebase Auth / Play Services Tasks ─────────────────────────────────────
-keep class com.google.android.gms.tasks.** { *; }

# ─── ML Kit Text Recognition ─────────────────────────────────────────────────
-keep class com.google.mlkit.** { *; }
-dontwarn com.google.mlkit.**

# ─── CameraX ─────────────────────────────────────────────────────────────────
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# ─── Hilt / Dagger ───────────────────────────────────────────────────────────
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }
-keepclassmembers class * {
    @javax.inject.Inject <init>(...);
    @javax.inject.Inject <fields>;
}

# ─── Kotlin Coroutines ───────────────────────────────────────────────────────
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-dontwarn kotlinx.coroutines.**

# ─── Coil (image loading) ────────────────────────────────────────────────────
-dontwarn coil.**

# ─── Jetpack Compose ─────────────────────────────────────────────────────────
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# ─── AndroidX / Lifecycle ────────────────────────────────────────────────────
-keep class androidx.lifecycle.** { *; }
-dontwarn androidx.lifecycle.**

# ─── Room ────────────────────────────────────────────────────────────────────
-keep class androidx.room.** { *; }
-keep @androidx.room.Entity class * { *; }
-keep @androidx.room.Dao interface * { *; }
-keep @androidx.room.Database class * { *; }
-keepclassmembers @androidx.room.Entity class * { *; }
-dontwarn androidx.room.**

# ─── Suppress warnings for missing classes in unused code paths ───────────────
-dontwarn javax.annotation.**
-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**