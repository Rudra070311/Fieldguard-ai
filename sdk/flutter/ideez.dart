import 'dart:convert';
import 'package:http/http.dart' as http;

class IDeezException implements Exception {
  final int statusCode;
  final String message;
  const IDeezException(
    this.statusCode,
    this.message,
  );

  @override
  String toString() =>
      'IDeezException($statusCode): $message';
}

class IDeezClient {
  final String apiKey;
  final String baseUrl;
  final Duration timeout;

  IDeezClient({
    required this.apiKey,
    this.baseUrl = 'https://api.ideez.dev',
    this.timeout = const Duration(seconds: 15),
  }) {
    if (apiKey.isEmpty) {throw ArgumentError('apiKey is required')}
  }

  Future<Map<String, dynamic>> health() async {
    return _request(
      '/health',
      method: 'GET',
    );
  }

  Future<Map<String, dynamic>> createSession(
    String userId, {
    Map<String, dynamic>? data,
  }) async {
    return _request(
      '/api/v1/sessions',
      method: 'POST',
      body: {
        'user_id': userId,
        ...?data,
      },
    );
  }

  Future<Map<String, dynamic>> verifyPin(
    String pin,
  ) async {
    return _request(
      '/api/v1/pin/verify',
      method: 'POST',
      body: {
        'pin': pin,
      },
    );
  }

  Future<Map<String, dynamic>> revokeSession(
    String sessionId,
  ) async {
    return _request(
      '/api/v1/sessions/$sessionId/revoke',
      method: 'POST',
    );
  }

  Future<Map<String, dynamic>> _request(
    String path, {
    required String method,
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse(
      '${baseUrl.replaceAll(RegExp(r'/+$'), '')}$path',
    );

    final headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $apiKey',
    };

    late http.Response response;

    switch (method) {
      case 'GET':
        response = await http
            .get(uri, headers: headers)
            .timeout(timeout);
        break;

      case 'POST':
        response = await http
            .post(
              uri,
              headers: headers,
              body: body == null ? null : jsonEncode(body),
            )
            .timeout(timeout);
        break;

      default:
        throw UnsupportedError(
          'Unsupported HTTP method: $method',
        );
    }

    final decoded = response.body.isEmpty
        ? <String, dynamic>{}
        : jsonDecode(response.body);

    if (response.statusCode < 200 ||
        response.statusCode >= 300) {
      throw IDeezException(
        response.statusCode,
        decoded.toString(),
      );
    }

    return Map<String, dynamic>.from(decoded);
  }
}