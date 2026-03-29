package com.example.e_comply.data.remote

import com.example.e_comply.BuildConfig
import com.google.android.gms.tasks.Tasks
import com.google.firebase.auth.FirebaseAuth
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * OkHttp interceptor that retrieves the current Firebase user's ID token
 * and attaches it as a Bearer token on every outbound request.
 * Requests without a signed-in user are sent without an Authorization
 * header so the server can return 401 and the app can redirect to login.
 */
class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val user = FirebaseAuth.getInstance().currentUser
        val token: String? = user?.let {
            try {
                // Synchronously wait for the token (runs on OkHttp's I/O thread)
                Tasks.await(it.getIdToken(false /* forceRefresh */)).token
            } catch (e: Exception) {
                null
            }
        }

        val request = chain.request().newBuilder().apply {
            token?.let { addHeader("Authorization", "Bearer $it") }
        }.build()

        return chain.proceed(request)
    }
}

object RetrofitClient {

    // BASE_URL is injected per build type via BuildConfig (see build.gradle.kts)
    private val BASE_URL = BuildConfig.BASE_URL

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        // Only log full request/response bodies in debug builds
        level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                else HttpLoggingInterceptor.Level.NONE
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor())    // auth token first
        .addInterceptor(loggingInterceptor)  // then logging
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}

