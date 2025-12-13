"""
Script de prueba para el sistema de gestión de capacidad
Prueba Feature Toggles y Throttling
"""
import asyncio
import httpx
import time
from typing import List, Dict
import json

# Configuración
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/v1"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


async def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_V1}/admin/health")
            data = response.json()
            
            print_info(f"Status: {data['status']}")
            print_info(f"CPU: {data['metrics']['cpu_percent']:.1f}%")
            print_info(f"Memoria: {data['metrics']['memory_percent']:.1f}%")
            print_info(f"Requests activos: {data['metrics']['active_requests']}")
            print_info(f"Throttle level: {data['metrics']['throttle_level']}")
            print_info(f"Throttle delay: {data['metrics']['throttle_delay_seconds']}s")
            
            if response.status_code == 200:
                print_success("Health check OK")
                return True
            else:
                print_error(f"Health check falló: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error en health check: {e}")
            return False


async def test_feature_toggles():
    """Test 2: Feature Toggles"""
    print_header("TEST 2: Feature Toggles")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Ver estado inicial
            print_info("Estado inicial de features:")
            response = await client.get(f"{API_V1}/admin/features")
            features = response.json()['features']
            for feature, enabled in features.items():
                status = "✓ Enabled" if enabled else "✗ Disabled"
                print(f"  {feature}: {status}")
            
            # 2. Desactivar transaction_delete
            print_info("\nDesactivando transaction_delete...")
            response = await client.post(f"{API_V1}/admin/features/transaction_delete/disable")
            if response.status_code == 200:
                print_success("transaction_delete desactivado")
            
            # 3. Verificar que está desactivado
            response = await client.get(f"{API_V1}/admin/features")
            if not response.json()['features']['transaction_delete']:
                print_success("Verificado: transaction_delete está desactivado")
            
            # 4. Intentar usar la feature (debería fallar)
            print_info("\nIntentando DELETE con feature desactivada...")
            response = await client.delete(f"{API_V1}/transactions/test123")
            if response.status_code == 503:
                print_success("DELETE bloqueado correctamente (503)")
            else:
                print_warning(f"DELETE devolvió: {response.status_code}")
            
            # 5. Reactivar feature
            print_info("\nReactivando transaction_delete...")
            response = await client.post(f"{API_V1}/admin/features/transaction_delete/enable")
            if response.status_code == 200:
                print_success("transaction_delete reactivado")
            
            # 6. Activar con TTL (10 segundos)
            print_info("\nDesactivando con TTL de 10 segundos...")
            await client.post(f"{API_V1}/admin/features/transaction_delete/disable")
            await client.post(
                f"{API_V1}/admin/features/transaction_delete/enable",
                json={"ttl": 10}
            )
            print_success("Feature activada con TTL de 10s")
            print_info("Esperando 11 segundos para verificar auto-desactivación...")
            await asyncio.sleep(11)
            
            response = await client.get(f"{API_V1}/admin/features")
            if not response.json()['features']['transaction_delete']:
                print_success("TTL funcionó: feature se desactivó automáticamente")
            else:
                print_warning("TTL no funcionó como esperado")
            
            # Restaurar estado
            await client.post(f"{API_V1}/admin/features/transaction_delete/enable")
            
            return True
            
        except Exception as e:
            print_error(f"Error en feature toggles: {e}")
            return False


async def test_emergency_mode():
    """Test 3: Modo Emergencia"""
    print_header("TEST 3: Modo Emergencia")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Ver estado inicial
            print_info("Estado antes de modo emergencia:")
            response = await client.get(f"{API_V1}/admin/features")
            before = response.json()['features']
            enabled_before = sum(1 for v in before.values() if v)
            print(f"  Features habilitadas: {enabled_before}/{len(before)}")
            
            # 2. Activar modo emergencia
            print_info("\nActivando modo emergencia...")
            response = await client.post(f"{API_V1}/admin/emergency/disable-non-critical")
            data = response.json()
            
            if response.status_code == 200:
                print_success("Modo emergencia activado")
                print_info("Estado de features:")
                for feature, enabled in data['features'].items():
                    status = "✓" if enabled else "✗"
                    critical = "(crítica)" if enabled else "(no crítica)"
                    print(f"  {status} {feature} {critical}")
            
            # 3. Verificar que operaciones no críticas están bloqueadas
            print_info("\nVerificando bloqueo de operaciones...")
            
            # DELETE debería estar bloqueado
            response = await client.delete(f"{API_V1}/transactions/test123")
            if response.status_code == 503:
                print_success("DELETE bloqueado (503)")
            
            # REVERT debería estar bloqueado
            response = await client.patch(f"{API_V1}/transactions/test123")
            if response.status_code == 503:
                print_success("REVERT bloqueado (503)")
            
            # 4. Restaurar modo normal
            print_info("\nRestaurando modo normal...")
            response = await client.post(f"{API_V1}/admin/emergency/restore")
            if response.status_code == 200:
                print_success("Modo normal restaurado")
            
            # Verificar restauración
            response = await client.get(f"{API_V1}/admin/features")
            after = response.json()['features']
            enabled_after = sum(1 for v in after.values() if v)
            print(f"  Features habilitadas: {enabled_after}/{len(after)}")
            
            return True
            
        except Exception as e:
            print_error(f"Error en modo emergencia: {e}")
            return False


async def test_throttling():
    """Test 4: Throttling con Carga"""
    print_header("TEST 4: Throttling bajo Carga")
    
    print_info("Generando 50 requests concurrentes...")
    print_warning("Esto puede tardar unos segundos...\n")
    
    async def make_request(client: httpx.AsyncClient, i: int) -> Dict:
        start_time = time.time()
        try:
            # Intentar crear transacción (puede fallar por validación, pero eso está OK)
            response = await client.post(
                f"{API_V1}/transactions",
                json={
                    "sender": f"user{i}",
                    "receiver": f"user{i+1}",
                    "quantity": 10.0
                },
                timeout=30.0
            )
            elapsed = time.time() - start_time
            return {
                "status": response.status_code,
                "elapsed": elapsed,
                "success": response.status_code in [200, 201, 400, 404]  # 400/404 son OK para este test
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": 0,
                "elapsed": elapsed,
                "success": False,
                "error": str(e)
            }
    
    async with httpx.AsyncClient() as client:
        # Lanzar requests concurrentes
        tasks = [make_request(client, i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Analizar resultados
        successful = sum(1 for r in results if r['success'])
        rejected = sum(1 for r in results if r['status'] == 503)
        errors = sum(1 for r in results if not r['success'] and r['status'] != 503)
        avg_time = sum(r['elapsed'] for r in results) / len(results)
        max_time = max(r['elapsed'] for r in results)
        
        print_info(f"Requests exitosos: {successful}/50")
        print_info(f"Requests rechazados (503): {rejected}/50")
        print_info(f"Errores: {errors}/50")
        print_info(f"Tiempo promedio: {avg_time:.2f}s")
        print_info(f"Tiempo máximo: {max_time:.2f}s")
        
        # Verificar métricas del sistema
        print_info("\nMétricas del sistema después de la carga:")
        response = await client.get(f"{API_V1}/admin/metrics")
        data = response.json()
        
        print(f"  CPU: {data['system']['cpu_percent']:.1f}%")
        print(f"  Memoria: {data['system']['memory_percent']:.1f}%")
        print(f"  Throttle level: {data['throttling']['level']}")
        print(f"  Throttle reason: {data['throttling']['reason']}")
        print(f"  Delay aplicado: {data['throttling']['delay_seconds']}s")
        
        if rejected > 0:
            print_success(f"Throttling funcionó: {rejected} requests rechazados")
        elif max_time > avg_time * 1.5:
            print_success("Throttling funcionó: delays detectados")
        else:
            print_warning("No se detectó throttling (carga insuficiente)")
        
        return True


async def test_metrics():
    """Test 5: Endpoint de Métricas"""
    print_header("TEST 5: Métricas Detalladas")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_V1}/admin/metrics")
            data = response.json()
            
            print_info("Métricas del Sistema:")
            print(f"  CPU: {data['system']['cpu_percent']:.1f}%")
            print(f"  Memoria: {data['system']['memory_percent']:.1f}%")
            
            print_info("\nRequests:")
            print(f"  Activos: {data['requests']['active']}")
            
            print_info("\nThrottling:")
            print(f"  Level: {data['throttling']['level']}")
            print(f"  Status: {data['throttling']['status']}")
            print(f"  Reason: {data['throttling']['reason']}")
            print(f"  Delay: {data['throttling']['delay_seconds']}s")
            
            print_info("\nFeatures:")
            for feature, enabled in data['features'].items():
                status = "✓" if enabled else "✗"
                print(f"  {status} {feature}")
            
            print_success("Métricas obtenidas correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error obteniendo métricas: {e}")
            return False


async def run_all_tests():
    """Ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 TEST SUITE: GESTIÓN DE CAPACIDAD                      ║")
    print("║  Throttling + Feature Toggles                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    results = []
    
    # Test 1: Health Check
    result = await test_health_check()
    results.append(("Health Check", result))
    await asyncio.sleep(1)
    
    # Test 2: Feature Toggles
    result = await test_feature_toggles()
    results.append(("Feature Toggles", result))
    await asyncio.sleep(1)
    
    # Test 3: Modo Emergencia
    result = await test_emergency_mode()
    results.append(("Modo Emergencia", result))
    await asyncio.sleep(1)
    
    # Test 4: Throttling
    result = await test_throttling()
    results.append(("Throttling", result))
    await asyncio.sleep(1)
    
    # Test 5: Métricas
    result = await test_metrics()
    results.append(("Métricas", result))
    
    # Resumen
    print_header("RESUMEN DE TESTS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests pasados{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TODOS LOS TESTS PASARON{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ ALGUNOS TESTS FALLARON{Colors.RESET}\n")


if __name__ == "__main__":
    print_info("Asegúrate de que el servicio esté corriendo en http://localhost:8001")
    print_info("Presiona Ctrl+C para cancelar\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests cancelados por el usuario{Colors.RESET}")
    except Exception as e:
        print_error(f"Error ejecutando tests: {e}")
